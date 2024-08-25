---
permalink: /
title: ""
excerpt: ""
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

{% if site.google_scholar_stats_use_cdn %}
{% assign gsDataBaseUrl = "https://cdn.jsdelivr.net/gh/" | append: site.repository | append: "@" %}
{% else %}
{% assign gsDataBaseUrl = "https://raw.githubusercontent.com/" | append: site.repository | append: "/" %}
{% endif %}
{% assign url = gsDataBaseUrl | append: "google-scholar-stats/gs_data_shieldsio.json" %}

<span class='anchor' id='about-me'></span>
<!-- {% include_relative includes/intro.md %} -->
# 🐑 About Me

I am now a final-year Ph.D. student at Sichuan University (四川大学), advised by [Yi Zhang(张意)](http://deepimaging.group/).  I'm also a visiting student at A*Star, advised by [Joey Tianyi Zhou](https://joeyzhouty.github.io/). I have published over 40 papers 
<a href='https://scholar.google.com/citations?user=2vZsJskAAAAJ'><img src="https://img.shields.io/endpoint?url={{ url | url_encode }}&logo=Google%20Scholar&labelColor=f6f6f6&color=9cf&style=flat&label=citations"></a>
<!-- <a href='https://scholar.google.com/citations?user=2vZsJskAAAAJ'><img src="https://img.shields.io/endpoint?logo=Google%20Scholar&url=https%3A%2F%2Fcdn.jsdelivr.net%2Fgh%2FZi-YuanYang%2Fzi-yuanyang.github.io@google-scholar-stats%2Fgs_data_shieldsio.json&labelColor=f6f6f6&color=9cf&style=flat&label=citations"> -->
 at the top journals/conferences such as IJCV, IEEE TIFS / TNNLS / TIM / TCSVT / TRPMS / TETC, IEEE JBHI/JSTSP, MICCAI, etc. Besides, I severed as a reviewer for several top journal/conferences, including IEEE TIFS/TMI, AIRE, AIME, EMNLP, MICCAI,etc.

I am currently seeking **postdoctoral** or **research fellow** opportunities. If you have any advice or are interested in exploring **academic collaborations**, please feel free to contact me at [cziyuanyang@gmail.com](mailto:cziyuanyang@gmail.com).  I look forward to your insights and suggestions.

My research interests includes:
- Biometrics
- Federated Learning
- AI in Healthcare
- Security and Privacy Analysis
- Dataset Distillation

<span class='anchor' id='news'></span>
{% include_relative includes/news.md %}

<span class='anchor' id='publications'></span>
{% include_relative includes/pub_short.md %}

<span class='anchor' id='honors'></span>
{% include_relative includes/honers.md %}

<span class='anchor' id='education'></span>
{% include_relative includes/education.md %}

<span class='anchor' id='service'></span>
{% include_relative includes/service.md %}

<span class='anchor' id='acknowledgement'></span>

# Acknowledgements
I would thank all my collaborators and advisors, they helped me a lot.