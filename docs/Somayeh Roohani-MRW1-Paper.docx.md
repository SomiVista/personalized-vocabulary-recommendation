VILNIUS GEDIMINAS TECHNICAL UNIVERSITY  
Faculty of Fundamental Sciences  
Department of Information Technologies

*Somayeh Roohani*

*ASMENINIŲ REKOMENDACIJŲ SISTEMŲ EKSPERIMENTINIS VERTINIMAS ŽODYNO MOKYMUISI DIRBTINIO INTELEKTO PAGRINDU VEIKIANČIOSE KALBŲ MOKYMO PLATFORMOSE*

*AN EXPERIMENTAL EVALUATION OF PERSONALIZED RECOMMENDER SYSTEMS FOR VOCABULARY LEARNING IN AI-DRIVEN LANGUAGE EDUCATION PLATFORMS*

Master’s Final Thesis 

*Engineering of Artificial Intelligence* 

*Informatics*

VILNIUS GEDIMINAS TECHNICAL UNIVERSITY  
Faculty of Fundamental Sciences  
Department of Information Technologies

*Somayeh Roohani*

*AN EXPERIMENTAL EVALUATION OF PERSONALIZED RECOMMENDER SYSTEMS FOR VOCABULARY LEARNING IN AI-DRIVEN LANGUAGE EDUCATION PLATFORMS*

Master’s Final Thesis

*Engineering of Artificial Intelligence studies*

*Informatics*

| Supervisor | *Professor, Dr. Irina Vinogradova-Zinkevič* |  |
| :---- | ----- | :---- |
|  |  |  |

**Contents**

[Introduction	2](#introduction)

[1\. Literature Review – Recommender Systems for Vocabulary Learning in AI‑Driven Education	4](#literature-review-–-recommender-systems-for-vocabulary-learning-in-ai‑driven-education)

[1.1. Evolution of Recommender Systems in Educational Contexts	4](#evolution-of-recommender-systems-in-educational-contexts)

[1.2. Deep Learning and Neural Recommender Models in Education	5](#deep-learning-and-neural-recommender-models-in-education)

[1.3. Vocabulary Recommendation and Language‑Focused Systems	6](#vocabulary-recommendation-and-language‑focused-systems)

[1.4. Collaborative Filtering, Cold‑Start and Out‑of‑Vocabulary Handling	7](#collaborative-filtering,-cold‑start-and-out‑of‑vocabulary-handling)

[1.5. Knowledge Graphs, GNNs and Learning Path Recommendation	8](#knowledge-graphs,-gnns-and-learning-path-recommendation)

[References	9](#references)

## **Introduction** {#introduction}

**Relevance of the research**. Vocabulary learning is one of the most demanding and time‑consuming parts of second language acquisition, yet many digital platforms still deliver vocabulary in a static, one‑size‑fits‑all way. Modern AI‑driven systems can track rich streams of learner behaviour, but it is not obvious which type of recommender algorithm uses this data best for personalised vocabulary support. Research in educational recommender systems shows that hybrid and deep learning approaches can significantly increase accuracy and learner satisfaction compared with simple methods, but most studies focus on courses or general resources, not on fine‑grained vocabulary items drawn from authentic media. At the same time, recent work on neural collaborative filtering, deep matrix factorisation, and sequence‑aware recommendation suggests that non‑linear models may capture complex learning patterns that traditional matrix factorisation cannot express.

The Subturtle platform represents a new type of language learning environment: it integrates with users’ browsing and streaming habits (e.g., YouTube and Netflix), extracts phrases from subtitles, and turns them into personalised practice materials supported by an AI coach. As Subturtle grows, its data becomes closer to large‑scale educational scenarios where cold‑start, sparsity, and out‑of‑vocabulary issues strongly influence the quality of recommendations. Research on educational recommenders and knowledge‑graph‑based systems confirms that poor handling of these effects leads to weaker personalisation and lower learning efficiency. However, there is still no systematic theoretical comparison of three key paradigms—Content‑Based Filtering, matrix factorisation–based Collaborative Filtering, and deep Autoencoder‑style models—applied specifically to vocabulary recommendation from authentic multimedia content.

This thesis addresses that gap by building a structured literature‑based comparison of these approaches in AI‑driven language education, with a focus on Subturtle’s vocabulary recommendation problem. The analysis draws on thirty recent studies on collaborative filtering, deep learning, educational recommender systems, vocabulary recommendation, cold‑start and out‑of‑vocabulary handling, and knowledge graphs in education.​

**Research problem** – Suboptimal personalisation of vocabulary recommendations in AI‑driven language learning platforms, due to the lack of a clear, evidence‑based choice between Content‑Based Filtering, matrix‑factorisation Collaborative Filtering, and deep Autoencoder models for this specific task.

**Research object** – Three recommender system approaches and their theoretical application to vocabulary learning in AI‑driven platforms: Content‑Based Filtering using vocabulary and context features, Collaborative Filtering based on matrix factorisation (including SVD‑type methods), and deep Autoencoder‑style models that learn non‑linear user–item representations.

**Research aim** – To theoretically evaluate and compare Content‑Based Filtering, matrix‑factorisation Collaborative Filtering, and deep Autoencoder models for personalised vocabulary recommendation in AI‑driven language education platforms, and to propose a framework for selecting and integrating the most appropriate approach in Subturtle.

**Objectives to achieve the aim**:

1. To carry out a structured literature review of recommender systems in education, with emphasis on matrix factorisation, deep learning, and hybrid approaches, and to summarise their reported strengths and limitations for personalisation.

2. To analyse how existing studies on vocabulary recommendation, cold‑start, and out‑of‑vocabulary handling inform the design of vocabulary recommenders that operate on phrases extracted from authentic multimedia content.

3. To develop a theoretical comparison framework, including relevant evaluation criteria and domain‑specific requirements, that can guide the choice between Content‑Based, SVD‑style Collaborative Filtering, and deep Autoencoder models for Subturtle.

**Research methods**.  The research uses a systematic literature review combined with comparative theoretical analysis. The literature review identifies and organises recent work on matrix factorisation, deep learning, hybrid recommender systems, vocabulary recommendation, cold‑start and out‑of‑vocabulary handling, and knowledge‑graph‑based personalisation in education. The theoretical analysis then compares Content‑Based Filtering, Collaborative Filtering, and deep Autoencoder models along dimensions such as cold‑start behaviour, data requirements, interpretability, scalability, suitability for vocabulary sequences, and integration with Subturtle’s data and system architecture.

1. ## **Literature Review – Recommender Systems for Vocabulary Learning in AI‑Driven Education** {#literature-review-–-recommender-systems-for-vocabulary-learning-in-ai‑driven-education}

   1. ### **Evolution of Recommender Systems in Educational Contexts** {#evolution-of-recommender-systems-in-educational-contexts}

      1. *From early educational recommenders to hybrid systems*

Early educational recommender systems were mainly simple content‑based or basic collaborative filtering tools that recommended courses or learning objects based on explicit ratings and prerequisite rules. As online learning expanded through learning management systems and MOOCs, researchers started to face new challenges such as data sparsity, cold‑start learners, and rapidly changing interests. To address these issues, hybrid systems that combine several recommendation techniques became more common in education.

A typical example is hybrid course or resource recommenders that merge collaborative filtering with content‑based information and clustering to increase accuracy and robustness. These systems usually integrate learner profiles, interaction logs, and resource attributes to generate personalised suggestions. Studies report that hybrid designs generally outperform single‑method systems in metrics such as precision, recall, MAE and ranking quality, especially when the learner base is diverse. This historical evolution shows that, in educational contexts, no single algorithm works best for all situations, and careful combination of methods is needed.

2. *Matrix factorisation and context‑aware approaches*

Matrix factorisation (MF) became a central technique in recommender systems after its success in commercial domains, and it was soon adapted to educational settings. MF projects users and items into a shared latent space and estimates preferences through inner products of latent factors, which makes it attractive for large, sparse educational datasets. Surveys of context‑aware collaborative filtering show that MF models have been extended to incorporate time, location, device, and other contextual variables, which improves recommendation relevance but also increases model complexity and data needs.

In education, MF‑based recommenders have been used for course recommendation, resource selection, and learning path support, often as part of hybrid frameworks. Context‑aware MF techniques allow systems to adapt recommendations to different stages of a course, changing learner performance, or learning scenarios such as distance education. However, MF still suffers from user cold‑start and item cold‑start, and it assumes mainly linear relations between latent factors, which may be too restrictive for complex learning behaviour. These limitations motivate the use of deep learning and other non‑linear models in educational recommendation.

2. ### **Deep Learning and Neural Recommender Models in Education** {#deep-learning-and-neural-recommender-models-in-education}

   1. *Neural collaborative filtering and deep CF*

Neural Collaborative Filtering (NCF) extends classical MF by replacing the inner product with a neural network that learns arbitrary interaction functions between users and items. This framework includes Generalised Matrix Factorisation, multilayer perceptron models, and combined architectures like NeuMF, which can capture both linear and non‑linear patterns in interaction data. Experiments on large datasets show that NCF‑type models systematically outperform traditional MF and BPR in top‑N ranking tasks, and that deeper architectures often yield better results when regularisation is applied.

Beyond NCF, many authors propose “deep CF” models that add convolutional, recurrent or autoencoder layers to the collaborative filtering process. Deep matrix factorisation and autoencoder‑based CF are able to represent complex non‑linear dependencies in sparse interaction matrices and can integrate side information such as content features or context vectors. In educational scenarios, these models are used to learn high‑quality embeddings of learners and learning items, often leading to higher precision, recall, and AUC than shallow methods for course or resource recommendation. At the same time, they require more data and computational resources, and their black‑box nature makes pedagogical explanation more difficult.

2. *Deep learning recommender systems in educational practice*

Deep learning has been widely adopted in educational recommender systems beyond generic CF, especially for course and activity recommendation. Some systems use recurrent neural networks and attention mechanisms to model the sequence of learner activities and to highlight the most informative past interactions when predicting next resources. Others apply convolutional networks or deep factorisation machines to fuse rich contextual and content features, for example in large university datasets or MOOC platforms.

A comprehensive survey of deep learning techniques in educational data mining shows that deep models are used for a wide range of tasks, including performance prediction, dropout detection, content analytics, and recommendation. The survey highlights their strengths in representation learning and multimodal integration, but it also notes challenges such as interpretability, fairness, and generalisation across institutions. In practice, deep educational recommenders tend to achieve higher accuracy than traditional methods when enough data are available, but they are not always ideal for new users, small courses, or situations that require clear justifications for recommendations. These trade‑offs are important when considering Autoencoder‑style models for vocabulary recommendation in platforms like Subturtle.

3. ### **Vocabulary Recommendation and Language‑Focused Systems** {#vocabulary-recommendation-and-language‑focused-systems}

   1. *Vocabulary relatedness, PWR and English‑specific recommenders*

Vocabulary recommendation is a specialised area that differs from general course or resource recommendation because of the large number of items, fine‑grained knowledge states, and strong contextual effects. One line of work studies vocabulary relatedness and how similarity between words or phrases can support better recommendation in sparse settings, for example by using co‑occurrence statistics, semantic embeddings, or graph structures. Another important contribution is the formalisation of Pedagogical Word Recommendation (PWR), where the system predicts whether a learner knows a given word based on the set of words already encountered.

PWR research uses large‑scale self‑reported vocabulary data from real learning services and applies collaborative filtering and neural models to model vocabulary knowledge states. Results show that neural CF improves F1‑scores compared to simple MF, but performance remains moderate due to granularity, context dependence, and forgetting effects in vocabulary learning. In parallel, several studies focus on English‑specific recommenders for learning resources and digital teaching materials, combining collaborative filtering with additional methods such as few‑shot learning or optimisation algorithms to address sparse interactions and new content. These systems demonstrate high precision and recall in recommending English learning resources but usually work with documents or exercises, not with short phrases taken from media subtitles.

2. *Domain characteristics of vocabulary learning from authentic media*

Vocabulary learning through authentic media, such as films, series or online videos, has specific characteristics that raise extra challenges for recommender design. Phrases taken from subtitles are often idiomatic, multi‑word and strongly dependent on audiovisual context, so representing them only as isolated tokens misses important information. In addition, learners may partially know some words in a phrase, may recognise a phrase receptively but not produce it, and may forget items over time, which makes preference signals noisy.

These characteristics suggest that good vocabulary recommenders for authentic media should combine several information sources: semantic representations of phrases, collaborative patterns across users, and possibly structured knowledge about concepts and relations. Knowledge‑graph‑based approaches, which link concepts, courses and resources in a graph and use graph neural networks or graph‑based metrics for recommendation, show promise for modelling rich relations in education, including language‑related domains. However, existing work typically focuses on course concepts and learning objects rather than fine‑grained vocabulary items, so further adaptation is needed for phrase‑level recommendation.

4. ### **Collaborative Filtering, Cold‑Start and Out‑of‑Vocabulary Handling** {#collaborative-filtering,-cold‑start-and-out‑of‑vocabulary-handling}

   1. *User cold‑start and sparse educational data*

Educational data are usually sparse: each learner interacts with only a small portion of available resources, and new users often have almost no history, which makes collaborative filtering difficult. A systematic review of the user cold‑start problem in recommendation systems shows that most solutions rely on auxiliary information such as user profiles, content features, or social links to initialise preferences. In educational contexts, studies combine demographic or curriculum information with early behaviour to produce initial recommendations before enough interaction data are collected.

Hybrid models that mix collaborative and content‑based signals are particularly effective at mitigating cold‑start in education. For example, user clustering based on learning preferences or programme information can reduce sparsity within clusters and improve the quality of neighbourhood‑based or MF‑based recommendations. In vocabulary learning, cold‑start is especially important because new users often want immediate suggestions, and there may be many new phrases appearing continuously in media streams. This situation supports the idea of combining Content‑Based Filtering, which works well from the first interactions, with collaborative and deep models, which improve performance once more data are available.

2. *Out‑of‑vocabulary, inductive settings and semantic cold‑start*

Out‑of‑vocabulary (OOV) handling in recommender systems refers to making predictions for users or items that were unseen during training, which is common in real‑world, inductive settings. A recent study evaluates nine OOV embedding strategies across several models and datasets and shows that naive methods like random OOV buckets create a large gap between transductive and inductive performance. Feature‑aware methods based on locality‑sensitive hashing and similarity in feature space prove more effective, improving inductive performance without harming standard performance.

For vocabulary recommendation, OOV appears when new words or phrases enter the system, or when new users start interacting with the platform. Semantic representations such as word or sentence embeddings, as well as ontology or knowledge‑graph structures, can help map OOV items to known regions of the feature space. Ontology‑based and knowledge‑graph‑based educational recommenders show how structured relations can be used to address pure cold‑start cases, for example by reasoning over concept hierarchies and related entities. In the context of Subturtle, combining phrase embeddings, semantic similarity, and possibly a vocabulary‑oriented knowledge graph could provide a principled way to recommend new phrases even when collaborative data are still limited.

5. ### **Knowledge Graphs, GNNs and Learning Path Recommendation** {#knowledge-graphs,-gnns-and-learning-path-recommendation}

   1. *Knowledge graphs and graph‑based recommenders in education*

Knowledge graphs represent entities (such as concepts, courses or resources) and their relations as nodes and edges, and are increasingly used in education for representation, recommendation and analytics. Systematic reviews of knowledge graph approaches in education show fast growth of this area, with applications in concept instruction, personalised learning, educational recommendation, and curriculum design. These studies indicate that knowledge graphs are built from diverse data sources such as course materials, student behaviour logs, and encyclopaedic resources, and that they are often combined with machine learning or semantic web technologies.​

Graph neural networks (GNNs) are a natural extension in this space, as they can learn representations over graph structures and support tasks like course and group recommendation. For example, some work uses GNNs to recommend MOOC learning groups and courses by modelling learners, courses and social ties in a heterogeneous graph. Other studies apply graph convolutional networks and sentence‑level embeddings to recommend knowledge concepts and related materials in MOOCs. These methods show that graph‑based models can capture complex relations among educational entities and support fine‑grained recommendations that respect curriculum structure and concept dependencies.

2. *Learning path and sequence‑aware recommendations*

Beyond recommending individual items, many educational systems aim to recommend whole learning paths that respect prerequisites, difficulty progression and learner goals. Some approaches combine clustering and sequence models to group similar learners and then learn typical paths within each group, which improves both accuracy and diversity of recommendations. Others incorporate graph‑based representations of curricula or concept maps into sequence models so that recommendations follow logical knowledge progressions.

For vocabulary learning, an analogous idea is to recommend sequences of words or phrases that build from simpler, high‑frequency items to more complex expressions, while revisiting earlier items to combat forgetting. Deep sequence models with attention, enriched by knowledge of concept relations or semantic similarity, can in principle support such personalised vocabulary paths. In a platform like Subturtle, where phrases come from authentic media, this would mean recommending phrases that are not only individually relevant but also form coherent, pedagogically meaningful trajectories through the learner’s viewing history and long‑term goals.

## **References** {#references}

1. Huang, W. (2025). Personalized recommendation of english learning resources based on collaborative filtering algorithm in english teaching scenarios. Discover Artificial Intelligence. [https://doi.org/10.1007/s44163-025-00638-6](https://doi.org/10.1007/s44163-025-00638-6)

2. Li, M. (2025). Research on the construction of English vocabulary learning recommendation system based on multi-objective crow search algorithm. Systems and Soft Computing. [https://doi.org/10.1016/j.sasc.2025.200304](https://doi.org/10.1016/j.sasc.2025.200304)

3. Lin, Y., Chen, H., Xia, W., Lin, F., Wang, Z., & Liu, Y. (2025). A comprehensive survey on deep learning techniques in educational data mining. Data Science and Engineering. [https://doi.org/10.1007/s41019-025-00303-z](https://doi.org/10.1007/s41019-025-00303-z)

4. Yang, X. (2025). Research on personalized distance education recommendation system based on deep learning. Scientific Reports. [https://doi.org/10.1038/s41598-025-26020-1](https://doi.org/10.1038/s41598-025-26020-1)

5. Abu-Salih, B., & Alotaibi, S. (2024). A systematic literature review of knowledge graph construction and application in education. Heliyon. [https://doi.org/10.1016/j.heliyon.2024.e25383](https://doi.org/10.1016/j.heliyon.2024.e25383)

6. Alatrash, R., Chatti, M. A., Ul Ain, Q., Fang, Y., Joarder, S., & Siepmann, C. (2024). ConceptGCN: Knowledge concept recommendation in MOOCs based on knowledge graph convolutional networks and SBERT. Computers and Education: Artificial Intelligence. [https://doi.org/10.1016/j.caeai.2023.100193](https://doi.org/10.1016/j.caeai.2023.100193)

7. Luo, Z., Wang, X., Wang, Y., Zhang, H., & Li, Z. (2024). A personalized MOOC learning group and course recommendation method based on graph neural network and social network analysis. [https://doi.org/10.48550/arXiv.2410.10658](https://doi.org/10.48550/arXiv.2410.10658)

8. Qu, K., Li, K. C., Wong, B. T. M., Wu, M. M. F., & Liu, M. (2024). A survey of knowledge graph approaches and applications in education. Electronics (Switzerland). [https://doi.org/10.3390/electronics13132537](https://doi.org/10.3390/electronics13132537)

9. Ma, Y., Ouyang, R., Long, X., Gao, Z., Lai, T., & Fan, C. (2023). DORIS: Personalized course recommendation system based on deep learning. PLoS ONE. [https://doi.org/10.1371/journal.pone.0284687](https://doi.org/10.1371/journal.pone.0284687)

10. Ma, Y., Wang, L., Zhang, J., Liu, F., & Jiang, Q. (2023). A personalized learning path recommendation method incorporating multi-algorithm. Applied Sciences (Switzerland). [https://doi.org/10.3390/app13105946](https://doi.org/10.3390/app13105946)

11. Safarov, F., Kutlimuratov, A., Abdusalomov, A. B., Nasimov, R., & Cho, Y. I. (2023). Deep learning recommendations of e-education based on clustering and sequence. Electronics (Switzerland). [https://doi.org/10.3390/electronics12040809](https://doi.org/10.3390/electronics12040809)

12. Yuan, H., & Hernandez, A. A. (2023). User cold start problem in recommendation systems: A systematic review. IEEE Access. [https://doi.org/10.1109/ACCESS.2023.3338705](https://doi.org/10.1109/ACCESS.2023.3338705)

13. Ahmadian Yazdi, H., Seyyed Mahdavi Chabok, S. J., & Kheirabadi, M. (2022). Dynamic educational recommender system based on improved recurrent neural networks using attention technique. Applied Artificial Intelligence. [https://doi.org/10.1080/08839514.2021.2005298](https://doi.org/10.1080/08839514.2021.2005298)

14. Dien, T. T., Thanh-Hai, N., & Thai-Nghe, N. (2022). An approach for learning resource recommendation using deep matrix factorization. Journal of Information and Telecommunication. [https://doi.org/10.1080/24751839.2022.2058250](https://doi.org/10.1080/24751839.2022.2058250)

15. Gao, M., Luo, Y., & Hu, X. (2022). Online course recommendation using deep convolutional neural network with negative sequence mining. Wireless Communications and Mobile Computing. [https://doi.org/10.1155/2022/9054149](https://doi.org/10.1155/2022/9054149)

16. Li, J. (2022). A recommendation model for college English digital teaching resources using collaborative filtering and few-shot learning technology. Computational Intelligence and Neuroscience. [https://doi.org/10.1155/2022/1233057](https://doi.org/10.1155/2022/1233057)

17. Zou, J. (2022). Intelligent course recommendation based on neural network for innovation and entrepreneurship education of college students. Informatica (Slovenia). [https://doi.org/10.31449/inf.v46i1.3776](https://doi.org/10.31449/inf.v46i1.3776)

18. Bhaskaran, S., Marappan, R., & Santhi, B. (2021). Design and analysis of a cluster-based intelligent hybrid recommendation system for e-learning applications. Mathematics. [https://doi.org/10.3390/math9020197](https://doi.org/10.3390/math9020197)

19. Joy, J., Raj, N. S., & Renumol, V. G. (2021). Ontology-based e-learning content recommender system for addressing the pure cold-start problem. Journal of Data and Information Quality. [https://doi.org/10.1145/3429251](https://doi.org/10.1145/3429251)

20. Li, Q., & Kim, J. (2021). A deep learning-based course recommender system for sustainable development in education. Applied Sciences (Switzerland). [https://doi.org/10.3390/app11198993](https://doi.org/10.3390/app11198993)

21. Zhu, Q. (2021). Network course recommendation system based on double-layer attention mechanism. Scientific Programming. [https://doi.org/10.1155/2021/7613511](https://doi.org/10.1155/2021/7613511)

22. Aljunid, M. F., & Dh, M. (2020). An efficient deep learning approach for collaborative filtering recommender system. Procedia Computer Science. [https://doi.org/10.1016/j.procs.2020.04.090](https://doi.org/10.1016/j.procs.2020.04.090)

23. Brasoveanu, A., Moodie, M., & Agrawal, R. (2020). Textual evidence for the perfunctoriness of independent medical reviews. CEUR Workshop Proceedings.

24. Rodriguez-Marin, P. A., Duque-Mendez, N. D., Ovalle-Carranza, D. A., & Martinez-Vargas, J. D. (2020). Personalized hybrid educational recommender system using matrix factorization with user and item information. [https://doi.org/10.20944/preprints202008.0700.v1](https://doi.org/10.20944/preprints202008.0700.v1)

25. Chen, X., Liu, H., Xu, Y., Yan, C., & Zhang, Q. (2019). Robust and privacy-preserving service recommendation over sparse data in education. Wireless Communications and Mobile Computing. [https://doi.org/10.1155/2019/2401857](https://doi.org/10.1155/2019/2401857)

26. Abdi, M. H., Okeyo, G. O., & Mwangi, R. W. (2018). Matrix factorization techniques for context-aware collaborative filtering recommender systems: A survey. Computer and Information Science. [http://dx.doi.org/10.5539/cis.v11n2p1](http://dx.doi.org/10.5539/cis.v11n2p1)

27. Bourkoukou, O., & El Bachari, E. (2018). Toward a hybrid recommender system for e-learning personalization based on data mining techniques. [https://dx.doi.org/10.30630/joiv.2.4.158](https://dx.doi.org/10.30630/joiv.2.4.158)

28. Pardos, Z., Fan, Z., & Jiang, W. (2018). Connectionist recommendation in the wild: On the utility and scrutability of neural networks for personalized course guidance. [https://doi.org/10.48550/arXiv.1803.09535](https://doi.org/10.48550/arXiv.1803.09535)

29. He, X., Liao, L., Zhang, H., Nie, L., Hu, X., & Chua, T. (2017). Neural collaborative filtering. In Proceedings of the 26th International World Wide Web Conference (pp. 173-182). International World Wide Web Conferences Steering Committee. [https://doi.org/10.1145/3038912.3052569](https://doi.org/10.1145/3038912.3052569)

30. Cheng, G., Gong, S., & Qu, Y. (2011). LNCS 7031 \- An empirical study of vocabulary relatedness and its application to recommender systems. Lecture Notes in Computer Science. [https://doi.org/10.1007/978-3-642-25073-6\_7](https://doi.org/10.1007/978-3-642-25073-6_7)

[image1]: <data:image/png;base64,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>