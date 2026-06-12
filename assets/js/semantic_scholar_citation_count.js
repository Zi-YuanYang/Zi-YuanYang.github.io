const citationCountElements = document.querySelectorAll("[data-paper-title]");

const normalizeTitle = (title) => {
    return (title || "")
        .toLowerCase()
        .normalize("NFKD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-z0-9]+/g, " ")
        .trim();
};

const scoreOpenAlexCandidate = (targetTitle, targetYear, candidate) => {
    const candidateTitle = candidate.display_name || candidate.title || "";
    const normalizedTarget = normalizeTitle(targetTitle);
    const normalizedCandidate = normalizeTitle(candidateTitle);
    let score = 0;

    if (!normalizedTarget || !normalizedCandidate) {
        return score;
    }

    if (normalizedTarget === normalizedCandidate) {
        score += 100;
    } else if (normalizedCandidate.includes(normalizedTarget) || normalizedTarget.includes(normalizedCandidate)) {
        score += 60;
    }

    const overlap = normalizedTarget.split(" ").filter((token) => normalizedCandidate.includes(token)).length;
    score += overlap;

    if (targetYear && candidate.publication_year && String(candidate.publication_year) === String(targetYear)) {
        score += 20;
    }

    return score;
};

const renderCitationBadge = (elements, citationData) => {
    elements.forEach((element) => {
        if (!citationData || typeof citationData.cited_by_count !== "number") {
            return;
        }
        const citationLabel = `${citationData.cited_by_count.toLocaleString()} citations`;
        const href = citationData.id || citationData.doi || "#";
        element.innerHTML = ` <a class="badge badge-pill badge-publication badge-info" href="${href}" target="_blank" rel="noopener noreferrer" title="Citation data from OpenAlex">${citationLabel}</a>`;
    });
};

const renderStaticCitationBadge = (element, citationCount) => {
    if (!citationCount || Number.isNaN(Number(citationCount))) {
        return false;
    }
    element.innerHTML = ` <span class="badge badge-pill badge-publication badge-info">${Number(citationCount).toLocaleString()} citations</span>`;
    return true;
};

const groups = new Map();
citationCountElements.forEach((element) => {
    if (renderStaticCitationBadge(element, element.getAttribute("data-paper-citations"))) {
        return;
    }
    const title = element.getAttribute("data-paper-title");
    const year = element.getAttribute("data-paper-year");
    if (!title) {
        return;
    }
    const key = `${title}|||${year || ""}`;
    if (!groups.has(key)) {
        groups.set(key, []);
    }
    groups.get(key).push(element);
});

const fetchOpenAlexCitation = async (title, year) => {
    const params = new URLSearchParams({
        filter: `display_name.search:${title}`,
        "per-page": "8",
        mailto: "cziyuanyang@gmail.com",
    });
    const response = await fetch(`https://api.openalex.org/works?${params.toString()}`);
    if (!response.ok) {
        throw new Error(`OpenAlex request failed: ${response.status}`);
    }
    const data = await response.json();
    const candidates = data.results || [];
    if (candidates.length === 0) {
        return null;
    }

    let bestCandidate = null;
    let bestScore = -1;
    candidates.forEach((candidate) => {
        const score = scoreOpenAlexCandidate(title, year, candidate);
        if (score > bestScore) {
            bestScore = score;
            bestCandidate = candidate;
        }
    });

    if (bestScore < 20) {
        return null;
    }

    return {
        id: bestCandidate.id,
        doi: bestCandidate.doi,
        cited_by_count: bestCandidate.cited_by_count || 0,
        year: bestCandidate.publication_year,
    };
};

const loadCitationCounts = async () => {
    for (const [key, elements] of groups.entries()) {
        const [title, year] = key.split("|||");
        const cacheKey = `openAlexCitation:${btoa(unescape(encodeURIComponent(key)))}`;
        const cachedData = localStorage.getItem(cacheKey);
        if (cachedData) {
            try {
                const parsed = JSON.parse(cachedData);
                if (Date.now() - parsed.timestamp < 7 * 24 * 60 * 60 * 1000) {
                    renderCitationBadge(elements, parsed.data);
                    continue;
                }
            } catch (error) {
                console.warn("Failed to parse cached OpenAlex citation data", error);
            }
        }

        try {
            const citationData = await fetchOpenAlexCitation(title, year);
            if (citationData) {
                localStorage.setItem(cacheKey, JSON.stringify({
                    data: citationData,
                    timestamp: Date.now(),
                }));
                renderCitationBadge(elements, citationData);
            }
        } catch (error) {
            console.warn(`Failed to fetch citation count for "${title}"`, error);
        }
    }
};

loadCitationCounts();
