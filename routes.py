from flask import Flask, request, jsonify
import logging
from pubmed import fetch_pubmed_data, fetch_details, parse_article_metadata, get_papers_by_date
from clustering import find_closest_papers, fuse_similar_clusters, perform_pca
from ai import generate_cluster_name, identify_trends_in_cluster
from cache import get_from_cache, save_to_cache

global global_query, global_max_records, global_presentdate, global_old_papers, global_new_papers, global_sim_tr
global_query = None
global_max_records = None
global_presentdate = None
global_old_papers = None
global_new_papers = None
global_sim_tr = None

global global_clusters, global_names
global_clusters = None

def initialize_routes(app):
    """
    Initialize routes for the Flask app and define a route to fetch articles.
    @param app - The Flask application
    The fetch_articles route handles POST requests and fetches articles based on the provided query.
    The function also interacts with global variables for query, max records, and present date.
    It logs the received request data and processes the query to fetch articles from cache or identify trends in clusters if not found in cache.
    """

    @app.route('/fetch_articles', methods=['POST'])
    def fetch_articles():
        """
        Fetch articles based on the query provided in the request JSON data. The articles are retrieved from PubMed data within a specified date range and maximum number of records. The article metadata is then parsed and grouped by date based on the present date provided in the request data.
        @return JSON response containing the grouped papers based on the present date.
        @param global_query - The query used to fetch articles.
        @param global_max_records - The maximum number of records to fetch.
        @param global_presentdate - The present date for grouping the papers.
        @param data - The JSON data received in the request.
        @raises Exception if an error occurs during the process.
        """
        global global_query, global_max_records, global_presentdate
        data = request.json
        logging.debug('Received request:', data)
        try:
            query = data['query']
            mindate = 2000
            maxdate = 2022
            max_records = int(data['max_records'])
            article_ids = fetch_pubmed_data(query, mindate, maxdate, max_records)
            xml_data = fetch_details(article_ids)
            articles_metadata = parse_article_metadata(xml_data)
            logging.debug('Fetched articles metadata:', articles_metadata)
            grouped_papers = get_papers_by_date(articles_metadata, int(data["presentdate"]))

            global_query = query
            global_max_records = max_records
            global_presentdate = data["presentdate"]

            return jsonify(grouped_papers)
        except Exception as e:
            logging.error('Error in /fetch_articles route:', e)
            return jsonify({'error': str(e)}), 500

    @app.route('/cluster_papers', methods=['POST'])
    def cluster_papers():
        """
        Cluster papers based on similarity and perform PCA on the results.
        @return A JSON response containing the clustered results and PCA results.
        """
        global global_query, global_max_records, global_presentdate, global_old_papers, global_new_papers, global_sim_tr
        global global_clusters
        data = request.json
        query = global_query
        max_papers = global_max_records
        present_year = global_presentdate
        new_papers = data['new_papers']
        old_papers = data['old_papers']
        global_new_papers = new_papers
        global_old_papers = old_papers
        sim_threshold = float(data['sim_threshold'])
        global_sim_tr = sim_threshold

        # Check cache first
        cached_result = get_from_cache(query, max_papers, present_year, new_papers, old_papers, sim_threshold)
        if cached_result:
            results = cached_result['clusters']
        else:
            results = find_closest_papers(new_papers, old_papers)
            results = fuse_similar_clusters(results, similarity_threshold=sim_threshold)
            save_to_cache(query, max_papers, present_year, new_papers, old_papers, sim_threshold, results, None, None)

        global_clusters = results
        pca_query_papers, pca_papers = perform_pca(results)

        return jsonify({'results': results, 'pca_results': {'query_papers': pca_query_papers, 'all_papers': pca_papers}})

    @app.route('/visualize_clusters', methods=['POST'])
    def visualize_clusters():
        """
        Visualize clusters of paper embeddings using PCA in a 3D plot.
        This function takes in JSON data containing clusters and combined papers, generates colors for each cluster, calculates PCA for the embeddings, and creates a 3D scatter plot for visualization.
        @return JSON response with a message indicating the success of the visualization.
        """
        data = request.json
        results_truncated = data['clusters']
        combined_papers = data['combined_papers']

        def generate_colors(num_colors):
            colors = []
            for i in range(num_colors):
                hue = i / num_colors
                lightness = 0.5
                saturation = 0.9
                color = mcolors.hsv_to_rgb((hue, saturation, lightness))
                colors.append(f'rgb({color[0]*255}, {color[1]*255}, {color[2]*255})')
            return colors

        all_embeddings = {}
        all_titles = []

        for query_title, similar_papers in results_truncated:
            query_abstract = next((p['abstract'] for p in combined_papers if p['title'] == query_title[0]), None)
            if query_abstract:
                all_embeddings[query_title[0]] = embed_text(query_abstract)
                all_titles.append(query_title[0])
            else:
                print(f"Abstract for query title '{query_title[0]}' not found.")

            for similar_title, _, _ in similar_papers:
                if similar_title not in all_embeddings:
                    similar_abstract = next((p['abstract'] for p in combined_papers if p['title'] == similar_title), None)
                    if similar_abstract:
                        all_embeddings[similar_title] = embed_text(similar_abstract)
                        all_titles.append(similar_title)
                    else:
                        print(f"Abstract for similar title '{similar_title}' not found.")

        if not all_embeddings:
            return jsonify({'error': 'No embeddings available to perform PCA.'}), 500

        embeddings_matrix = torch.stack(list(all_embeddings.values())).numpy()
        pca = PCA(n_components=3)
        reduced_embeddings = pca.fit_transform(embeddings_matrix)
        paper_to_coords = dict(zip(all_titles, reduced_embeddings))

        traces = []
        num_queries = len(results_truncated)
        colors = generate_colors(num_queries)

        for idx, (query, similar_papers) in enumerate(results_truncated):
            query_coords = paper_to_coords.get(query[0], [0, 0, 0])
            query_trace = go.Scatter3d(
                x=[query_coords[0]], y=[query_coords[1]], z=[query_coords[2]],
                mode='markers',
                marker=dict(size=10, color=colors[idx]),
                name=f'Query {idx + 1}'
            )
            traces.append(query_trace)
            
            for title, _, _ in similar_papers:
                paper_coords = paper_to_coords.get(title, [0, 0, 0])
                paper_trace = go.Scatter3d(
                    x=[paper_coords[0]], y=[paper_coords[1]], z=[paper_coords[2]],
                    mode='markers',
                    marker=dict(size=5, symbol='diamond', color=colors[idx]),
                    showlegend=False
                )
                traces.append(paper_trace)

        layout = go.Layout(
            title="3D PCA Visualization of Paper Embeddings",
            scene=dict(
                xaxis=dict(title='PCA Component 1'),
                yaxis=dict(title='PCA Component 2'),
                zaxis=dict(title='PCA Component 3')
            ),
            legend=dict(
                title="Query Papers",
                itemsizing='constant',
                x=1.05,
                xanchor='left',
                orientation='v'
            ),
            margin=dict(l=0, r=0, b=0, t=30)
        )
        fig = go.Figure(data=traces, layout=layout)
        fig.show()
        return jsonify({'message': 'Visualization generated successfully.'})

    @app.route('/generate_cluster_names', methods=['POST'])
    def generate_cluster_names():
        """
        Generate cluster names based on the input clusters. If the cluster names are already cached, retrieve them from the cache; otherwise, generate new cluster names and save them to the cache.
        @return A JSON response containing the cluster names.
        """
        global global_query, global_max_records, global_presentdate, global_old_papers, global_new_papers, global_sim_tr
        global global_clusters, global_names
        data = request.json
        clusters = data['clusters']
        cluster_names = []

        cached_result = get_from_cache(global_query, global_max_records, global_presentdate, global_new_papers, global_old_papers, global_sim_tr)
        if cached_result and cached_result['cluster_names'] != None:
            cluster_names = cached_result['cluster_names']
        else:   
            for cluster in clusters:
                cluster_name = generate_cluster_name(cluster)
                cluster_names.append(cluster_name)
                save_to_cache(global_query, global_max_records, global_presentdate, global_new_papers, global_old_papers, global_sim_tr, global_clusters, cluster_names, None)

        global_names = cluster_names  

        return jsonify(cluster_names)

    @app.route('/identify_trends', methods=['POST'])
    def identify_trends():
        """
        Identify trends based on the clusters provided in the input data. If the trends are already cached, retrieve them; otherwise, identify trends for each cluster and save the results to the cache.
        @return A JSON response containing the identified trends.
        """
        global global_query, global_max_records, global_presentdate, global_old_papers, global_new_papers, global_sim_tr
        global global_clusters, global_names
        data = request.json
        clusters = data['clusters']
        trends = []

        cached_result = get_from_cache(global_query, global_max_records, global_presentdate, global_new_papers, global_old_papers, global_sim_tr)
        if cached_result and cached_result['trends'] != None:
            trends = cached_result['trends']
        else:   
            for cluster in clusters:
                trend = identify_trends_in_cluster(cluster)
                trends.append(trend)
            save_to_cache(global_query, global_max_records, global_presentdate, global_new_papers, global_old_papers, global_sim_tr, global_clusters, global_names, trends)

        return jsonify(trends)