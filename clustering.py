import torch
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import numpy as np
from ai import embed_text

def modified_dbscan(X, core_indices, eps, min_samples):
    """
    Implement a modified DBSCAN clustering algorithm.
    @param X - The dataset
    @param core_indices - Indices of core points in the dataset
    @param eps - The maximum distance between two samples for one to be considered as in the neighborhood of the other
    @param min_samples - The number of samples in a neighborhood for a point to be considered as a core point
    @return The cluster labels for each point in the dataset
    """
    labels = -np.ones(len(X), dtype=int)  # Initialize all points as noise with integer type
    cluster_id = 0

    for idx in core_indices:
        if labels[idx] != -1:  # Skip if already processed
            continue

        # Find neighbors
        neighbors = np.where(np.linalg.norm(X - X[idx], axis=1) < eps)[0]

        if len(neighbors) < min_samples:
            labels[idx] = -1  # Still noise, but this is redundant
        else:
            labels[idx] = cluster_id
            expand_cluster(X, labels, cluster_id, neighbors, eps, min_samples)
            cluster_id += 1

    return labels

def expand_cluster(X, labels, cluster_id, neighbors, eps, min_samples):
    """
    Expand the cluster by assigning cluster IDs to neighboring points.
    @param X - Data points
    @param labels - Cluster labels
    @param cluster_id - ID of the cluster being expanded
    @param neighbors - Neighboring points
    @param eps - Maximum distance between two samples for one to be considered as in the neighborhood of the other
    @param min_samples - The number of samples in a neighborhood for a point to be considered as a core point
    """
    i = 0
    while i < len(neighbors):
        neighbor_idx = neighbors[i]

        if labels[neighbor_idx] == -1:  # Noise
            labels[neighbor_idx] = cluster_id

        elif labels[neighbor_idx] == -2:  # Unclassified
            labels[neighbor_idx] = cluster_id
            new_neighbors = np.where(np.linalg.norm(X - X[neighbor_idx], axis=1) < eps)[0]
            if len(new_neighbors) >= min_samples:
                neighbors = np.append(neighbors, new_neighbors)  # Append new neighbors

        i += 1

def find_closest_papers(query_papers, all_papers, initial_eps=11, min_samples=0):
    """
    Find the closest papers to a set of query papers from a pool of all papers.
    @param query_papers - The papers to use as queries
    @param all_papers - The pool of all papers to search from
    @param initial_eps - The initial value for epsilon in DBSCAN clustering
    @param min_samples - The minimum number of samples required for a cluster
    @return A list of tuples containing query information and the closest papers, along with EPS values used for each cluster.
    """
    if not query_papers or not all_papers:
        return []
    
    if len(query_papers) > 10:
        query_papers = query_papers[:10]

    query_vecs = []
    for paper in query_papers:
        embedded_text = embed_text(paper['abstract'])
        if embedded_text is not None:
            query_vecs.append(embedded_text)

    if not query_vecs:
        return []

    query_vecs = torch.stack(query_vecs)
    all_paper_vecs = []
    all_paper_texts = []
    for paper in all_papers:
        embedded_text = embed_text(paper['abstract'])
        if embedded_text is not None:
            all_paper_vecs.append(embedded_text)
            all_paper_texts.append(paper['abstract'])

    if not all_paper_vecs:
        return []

    all_paper_vecs = torch.stack(all_paper_vecs)
    all_paper_vecs_np = all_paper_vecs.numpy()

    core_indices = list(range(len(query_papers)))
    eps = initial_eps
    labels = modified_dbscan(all_paper_vecs_np, core_indices, eps, min_samples)

    # Adjust eps for clusters with more than 30 data points
    eps_log = []
    for cluster_id in range(max(labels) + 1):
        cluster_indices = np.where(labels == cluster_id)[0]
        while len(cluster_indices) > 40 and eps > 0:
            eps -= 0.5
            labels = modified_dbscan(all_paper_vecs_np, core_indices, eps, min_samples)
            cluster_indices = np.where(labels == cluster_id)[0]
        eps_log.append((cluster_id, eps))

    best_assignments = {}
    for i, query_paper in enumerate(query_papers):
        cluster_id = labels[core_indices[i]]
        if cluster_id == -1:
            continue

        cluster_indices = np.where(labels == cluster_id)[0]
        for index in cluster_indices:
            similarity_score = cosine_similarity([query_vecs[i].numpy()], [all_paper_vecs_np[index]])[0][0]
            paper_title = all_papers[index]['title']
            if paper_title not in best_assignments or best_assignments[paper_title][1] < similarity_score:
                best_assignments[paper_title] = (query_paper['title'], similarity_score)

    results = {query['title']: [] for query in query_papers}
    for paper_title, (query_title, _) in best_assignments.items():
        paper_abstract = next(p['abstract'] for p in all_papers if p['title'] == paper_title)
        similarity_score = best_assignments[paper_title][1]
        results[query_title].append((paper_title, paper_abstract, similarity_score))

    final_results = []
    for query_paper in query_papers:
        query_info = (query_paper['title'], query_paper['abstract'])
        closest_papers = sorted(results[query_paper['title']], key=lambda x: x[2], reverse=True)
        final_results.append((query_info, closest_papers))

    # Log eps values used for each cluster
    print('EPS values used for each cluster:', eps_log)

    return final_results

def fuse_similar_clusters(final_results, similarity_threshold=0.8):
    """
    Fuse similar clusters based on a similarity threshold.
    @param final_results - the final results to be clustered
    @param similarity_threshold - the threshold for considering clusters as similar (default is 0.8)
    """
    # Dictionary to store average embeddings of each cluster
    cluster_embeddings = {}
    
    # Calculate average embeddings for each cluster
    for (query_title, query_abstract), papers in final_results:
        embeddings = [embed_text(paper[1]) for paper in papers]
        if embeddings:
            avg_embedding = torch.mean(torch.stack(embeddings), dim=0)
            cluster_embeddings[query_title] = avg_embedding

    # Create titles list and embeddings matrix
    titles = list(cluster_embeddings.keys())
    embeddings_matrix = torch.stack(list(cluster_embeddings.values())).numpy()
    
    # Compute similarity matrix
    similarity_matrix = cosine_similarity(embeddings_matrix)

    # Identify clusters to merge based on similarity threshold
    to_merge = {}
    for i in range(len(titles)):
        for j in range(i + 1, len(titles)):
            if similarity_matrix[i][j] > similarity_threshold:
                cluster_i_size = len(final_results[i][1])
                cluster_j_size = len(final_results[j][1])
                if cluster_i_size + cluster_j_size <= 40:
                    smaller, larger = sorted([i, j], key=lambda x: -len(final_results[x][1]))
                    to_merge[titles[smaller]] = titles[larger]

    # Dictionary to store merged clusters
    merged_clusters = {}
    for (query_title, query_abstract), papers in final_results:
        root_title = to_merge.get(query_title, query_title)
        if root_title not in merged_clusters:
            merged_clusters[root_title] = [[query_title], (query_title, query_abstract), []]
        else:
            merged_clusters[root_title][0].append(query_title)
        merged_clusters[root_title][2].extend(papers)
        # Include the key (title, abstract) of the absorbed cluster into the merged cluster
        if root_title != query_title:
            merged_clusters[root_title][2].append((query_title, query_abstract, 1.0)) # Adding a default similarity score

    # Convert merged_clusters dictionary to list
    new_final_results = list(merged_clusters.values())

    # Sort papers within each cluster by the third element (similarity score) in descending order
    for cluster in new_final_results:
        cluster[2].sort(key=lambda x: x[2], reverse=True)

    # Convert similarity scores to float for consistency
    for cluster in new_final_results:
        cluster[2] = [(title, abstract, float(similarity)) for (title, abstract, similarity) in cluster[2]]

    # Log the clusters formed in the backend
    print('Clusters formed:', new_final_results)

    return new_final_results

def perform_pca(clusters):
    """
    Perform Principal Component Analysis (PCA) on the given clusters to reduce dimensionality.
    @param clusters - list of clusters containing papers
    @return PCA results for all papers and query papers
    """
    all_papers = []
    query_papers = []

    for cluster in clusters:
        query_papers.extend(cluster[0])  # Add all query papers
        all_papers.extend(cluster[2])    # Add all papers in the cluster

    abstracts = [paper[1] for paper in all_papers]
    embeddings = [embed_text(abstract) for abstract in abstracts]
    embeddings_matrix = torch.stack(embeddings).numpy()

    pca = PCA(n_components=3)
    pca_results = pca.fit_transform(embeddings_matrix)

    pca_papers = []
    for idx, (title, abstract, similarity) in enumerate(all_papers):
        pca_papers.append({
            'title': title,
            'coords': pca_results[idx].tolist()
        })

    pca_query_papers = []
    for idx, title in enumerate(query_papers):
        pca_query_papers.append({
            'title': title,
            'coords': pca_results[idx].tolist()
        })

    return pca_query_papers, pca_papers