import sqlite3
import json

def update_cache_for_sim_threshold_8():
    """
    Update the cluster_names and trends in the cache where sim_threshold equals 8.
    """
    # The new cluster names to be updated
    cluster_names = [
        "Food Safety and Contamination",
        "Environmental Contamination and Remediation Research",
        "Food Safety and Antibacterial Measures",
        "Environmental Contaminants and Food Safety Analysis",
        "Chemical Contamination in Food Packaging and Environmental Consequences"
    ]
    
    # The new trends to be updated
    trends = [
        """- <b>Emerging topic, a new topic, new field of study never seen before</b>: The assessment of per- and polyfluoroalkyl substances (PFAS) in freshwater fish across the United States, specifically the potential contribution of PFOS from consumption of locally caught freshwater fish to serum levels, and its implications on environmental justice and public health / Importance degree: High\n
        - <b>Regulatory Changes</b>: The need for upgraded regulation frameworks to consider new products and dietary patterns, exemplified by the risk-benefit assessment of shifting from traditional meat-based diets to alternative dietary patterns, and the implementation of food matrix effects into chemical food contaminant risk assessment / Importance degree: High\n
        - <b>Methodological innovations</b>: The development of a rapid and sensitive supercritical fluid chromatography (SFC)-MS method to determine two typical oxygenated PAHs in liquid milks for assessing their health quality / Importance degree: Medium\n
        - <b>Public Health Concerns</b>: The application of plant-derived polyphenols as Nrf2 activators to counteract oxidative stress and intestinal toxicity induced by mycotoxins in swine, and the investigation of household fuel usage and its association with acute respiratory infection in children in Bangladesh / Importance degree: Medium\n"
        - <b>Risk Assessment and Management</b>: The lack of evidence on the best approach for accurate detection of aflatoxin levels in corn and the need for fit-for-purpose sampling procedures to obtain reliable results, as well as the characterization of public health risks from snail meat consumption in Cameroon, and the assessment of the microbial quality of water used for handwashing and hygienic practice in Ethiopia / Importance degree: Medium""",
        
        """- <b>Methodological innovations</b>: The use of metal-organic frameworks (MOFs) for extraction and delivery of pesticides and agrochemicals is an emerging trend in agricultural research. MOFs have shown potential due to their versatile and highly porous structure, offering a better alternative to conventionally used porous materials. The latest studies on the use of MOFs for targeted delivery and pesticide control indicate a shift towards adopting innovative materials for environmental remediation and agricultural applications. / Importance degree: High\n
        - <b>Environmental impact</b>: There is a growing focus on the utilization of waste products, such as jackfruit waste, for the production of value-added products and their potential applications. This trend signifies a shift towards sustainable waste management and reduced environmental impact in various industries. The review addresses the feasibility of valorizing waste to produce value-added products, ultimately contributing to waste reduction and environmental protection in a sustainable manner. / Importance degree: Medium\n
        - <b>Technological advances</b>: The use of mesoporous activated carbon for efficient dye adsorption presents a technological advancement in the field of environmental remediation. The synthesis of activated carbon from crop residues for the removal of contaminants from wastewater reflects a shift towards the development of innovative and eco-friendly techniques for pollution control. / Importance degree: Medium\n
        - <b>Shift of focus on a specific domain</b>: Research on potentially toxic trace metals in home environments has gained attention, especially in the context of understanding the sources, pathways, and concentrations of trace metals indoors and their relationship to outdoor soils. This shift highlights a growing emphasis on investigating indoor environmental quality and its potential impact on human health. / Importance degree: Medium\n
        - <b>Emerging topic, a new topic, new field of study never seen before</b>: The study on the metabolism of non-food, lignocellulosic plant material for mixotrophic growth of microalgae constitutes an emerging topic. This approach demonstrates advantages over traditional carbon sources, signifying a novel field of study in the utilization of non-food plant biomass for sustainable microalgae growth. / Importance degree: Low\n
        - <b>Geographical shifts</b>: The identification of the sources and fate of trace metals between outdoor and indoor environments in Sydney, Australia, signifies a geographical shift in environmental research. This shift suggests a localized focus on understanding potentially toxic trace metal exposures in the home environment within a specific geographical context. / Importance degree: Low""",
        
        """- <b>Technological advances</b>: The use of enzymatic extraction techniques for the production of pure and intact fucoidans from brown seaweeds illustrates a technological advancement in the field of food safety and bioactive compound extraction, with potential applications in pharmaceutical and nutraceutical industries. / Importance degree: High\n
        "- <b>Methodological innovations</b>: The utilization of electrochemical methods for detecting food contaminants using carbon nanomaterial-based electrodes represents a methodological innovation in food safety analysis. This approach provides simplicity, ease of handling, and specificity in determining food safety, offering potential improvements in food quality control. / Importance degree: Medium\n
        "- <b>An increase of papers talking about the same topic</b>: There is an increase in research papers focusing on biofilm formation by pathogenic microorganisms and the development of antibiofilm approaches to inhibit and eradicate biofilms from foods and food processing surfaces. This indicates a growing interest in addressing the challenges posed by biofilm-associated food contamination. / Importance degree: Medium\n
        "- <b>Environmental impact</b>: The study on antimicrobial resistance in marine bivalves sheds light on the environmental impact of antibiotic resistance in aquatic ecosystems and its potential implications for human health through contaminated seafood consumption. This reflects a concern for environmental and public health aspects of food safety. / Importance degree: Medium\n
        "- <b>Consumer behavior and consumption</b>: The prevalence of antibiotic-resistant bacteria in raw meat sold in Accra, Ghana, emphasizes the potential impact of consumer behavior and consumption patterns on the dissemination of multidrug-resistant bacteria through animal source foods, highlighting public health implications. / Importance degree: Low""",
        
        """- <b>Regulatory Changes</b>: The studies focusing on the safety assessment of recycling processes for post-consumer PET into food contact materials reflect a pivotal regulatory change in the food safety sector, demonstrating an increased emphasis on ensuring the safety of recycled materials. These changes are of High importance, demanding immediate attention to promote sustainable food packaging.\n
        - <b>Public Health Concerns</b>: The research on the biodegradation of ochratoxin A by endophytic Trichoderma koningii strains and the study on aflatoxins in feed for swine underscore the ongoing concern over mycotoxin contamination and its potential impact on human and animal health. These public health concerns are of High importance, necessitating immediate measures to mitigate potential health risks associated with mycotoxins in the food chain.\n
        - <b>Technological Advances</b>: Studies exploring the optimization and validation of analytical methods, such as the LC-MS/MS method for pesticide residue determination and the assessment of microfibers using advanced techniques like LC-MS/MS and FTIR, demonstrate a notable trend towards technological advancements in analytical methodologies. These advances are of Medium importance, indicating a shift towards enhancing the precision and efficiency of analytical processes in food safety research.""",
        
        """- <b>Environmental impact</b>: The analysis of newer academic papers indicates a significant emphasis on environmental impact, particularly with regards to bioaccumulation and migration of hazardous substances such as PFAS, mycotoxins, and heavy metals. The importance score for this trend is High. The shift of focus towards understanding the impact of environmental pollutants on ecosystems, food safety, and human health highlights the urgency of addressing these emerging environmental challenges.\n
        - <b>Public Health Concerns</b>: A major shift is observed towards researching the toxicity and effects of various substances on public health, particularly regarding food safety. Research papers focus on studying the health risks associated with the consumption of contaminated foods, from pesticides and mycotoxins to heavy metals and environmental pollutants like PFAS. This trend is of High importance, as it directly impacts public health and necessitates immediate attention and awareness to mitigate these risks.\n
        - <b>Methodological innovations</b>: The emergence of machine learning, big data analytics, and genomic techniques for the analysis of contaminants and their impact on food safety is a prominent trend within the dataset. This methodological innovation is of Medium importance as it presents new opportunities for more accurate and efficient analysis of food safety and environmental contaminants.\n
        - <b>An increase of papers talking about the same topic</b>: The dataset also depicts an increase in research papers focusing on the same or related topics, such as the bioaccumulation of PFAS and other contaminants, effectiveness of adsorbent materials for pollutant removal, and the impact of heavy metals on crop production. This trend is of Medium importance, highlighting the ongoing and expanding research in these critical areas.\n
        - <b>Regulatory Changes</b>: There is a noticeable theme centered around the need for regulatory changes and monitoring of harmful substances in food contact materials. This reflects a growing concern within the academic community for stricter regulation and monitoring of contaminants in food packaging materials, especially PFAS and OPEs. The importance of this trend is Low"""    
        ]
    
    # Convert cluster_names and trends to JSON format
    cluster_names_json = json.dumps(cluster_names)
    trends_json = json.dumps(trends)
    
    # Connect to the SQLite database
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()
    
    # Update the rows where sim_threshold is 8
    cursor.execute('''
        UPDATE cache
        SET cluster_names = ?, trends = ?
        WHERE ROWID = (
            SELECT ROWID FROM cache
            LIMIT 1 OFFSET 1
        )
    ''', (cluster_names_json, trends_json))
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

# Call the function to update the database
update_cache_for_sim_threshold_8()
