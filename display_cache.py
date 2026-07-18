import sqlite3
import json

def display_cache():
    """
    Display the contents of the cache database table.
    @return None
    """
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cache')
    rows = cursor.fetchall()
    
    for row in rows:
        query, max_papers, present_year, new_papers, old_papers, sim_threshold, clusters, cluster_names, trends = row
        print(f"Query: {query}")
        print(f"Max Papers: {max_papers}")
        print(f"Present Year: {present_year}")
        print(f"New Papers: {json.loads(new_papers)}")
        print(f"Old Papers: {json.loads(old_papers)}")
        print(f"Similarity Threshold: {sim_threshold}")
        print(f"Clusters: {json.loads(clusters)}")
        print(f"Cluster Names: {json.loads(cluster_names)}")
        print(f"Trends: {json.loads(trends)}")
        print("-" * 50)
    
    conn.close()

if __name__ == "__main__":
    display_cache()
