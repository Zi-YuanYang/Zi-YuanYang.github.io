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
{% include_relative includes/intro.md %}

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

<script type='text/javascript' id='clustrmaps' src='//cdn.clustrmaps.com/map_v2.js?cl=ffffff&w=a&t=tt&d=wezK_VMGs_K-oi1KTL4B-DFRRuq_XpZcmidpdoc9WK0'></script>
