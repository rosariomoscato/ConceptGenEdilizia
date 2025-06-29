document.addEventListener('DOMContentLoaded', () => {
    const archiveGrid = document.getElementById('archiveGrid'); 
    
    // Header links - using direct hrefs in HTML is simpler, so JS listeners for these are commented out.
    // const homeLinkButtonArchive = document.getElementById('homeLinkButtonArchivePage'); 
    // const helpLinkButtonArchive = document.getElementById('headerHelpLinkArchivePage'); 
    // if (homeLinkButtonArchive) {
    //     homeLinkButtonArchive.addEventListener('click', (e) => {
    //         e.preventDefault(); 
    //         window.location.href = homeLinkButtonArchive.href; 
    //     });
    // }
    // if (helpLinkButtonArchive) {
    //     helpLinkButtonArchive.addEventListener('click', (e) => {
    //         e.preventDefault();
    //         window.location.href = helpLinkButtonArchive.href;
    //     });
    // }

    async function fetchAndDisplayArchive() {
        if (!archiveGrid) {
            console.error("Archive grid container not found.");
            return;
        }
        // Updated loading message to match dark theme
        archiveGrid.innerHTML = '<p class="text-center col-span-full p-5 text-slate-400">Loading archived concepts...</p>';

        try {
            const response = await fetch('/api/archive');
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const concepts = await response.json();

            if (concepts.length === 0) {
                archiveGrid.innerHTML = '<p class="text-center col-span-full p-5 text-slate-400">No concepts have been archived yet.</p>';
                return;
            }

            archiveGrid.innerHTML = ''; 

            concepts.forEach(concept => {
                const conceptCard = document.createElement('div');
                // Updated card background and text colors for dark theme
                conceptCard.className = 'flex flex-col gap-3 pb-3 bg-slate-800 p-4 rounded-lg shadow-lg hover:shadow-cyan-500/30 transition-shadow'; 

                let imagesHTML = '<div class="w-full bg-slate-700 aspect-video rounded-xl flex items-center justify-center"><p class="text-slate-500 text-sm">No image</p></div>';
                if (concept.gemini_image_urls && concept.gemini_image_urls.length > 0) {
                    imagesHTML = `
                        <div
                          class="w-full bg-center bg-no-repeat aspect-video bg-cover rounded-xl border border-slate-700"
                          style="background-image: url('${concept.gemini_image_urls[0]}');"
                          aria-label="Visualization for ${concept.prompt}"
                        ></div>`;
                }
                
                let flowiseHTML = '<p class="text-slate-400">No detailed concept text.</p>';
                if (concept.flowise_response) {
                    if (typeof marked !== 'undefined') {
                        flowiseHTML = marked.parse(concept.flowise_response);
                    } else {
                        const escapedText = concept.flowise_response
                            .replace(/&/g, "&amp;")
                            .replace(/</g, "&lt;")
                            .replace(/>/g, "&gt;")
                            .replace(/"/g, "&quot;")
                            .replace(/'/g, "&#039;");
                        flowiseHTML = `<div class="whitespace-pre-wrap">${escapedText}</div>`;
                    }
                }

                const textContentHTML = `
                    <div>
                        <h3 class="text-slate-100 text-base font-semibold leading-tight truncate mb-1" title="${concept.prompt}">Prompt: ${concept.prompt}</h3>
                        <div class="text-slate-300 text-sm font-normal leading-normal max-h-32 overflow-y-auto prose prose-sm prose-invert max-w-none mb-2 border border-slate-700 p-2 rounded bg-slate-900">
                           ${flowiseHTML}
                        </div>
                        <p class="text-slate-500 text-xs mt-1">Archived: ${new Date(concept.timestamp).toLocaleString()}</p>
                    </div>
                `;

                conceptCard.innerHTML = imagesHTML + textContentHTML;
                archiveGrid.appendChild(conceptCard);
            });

        } catch (error) {
            console.error("Error fetching archive:", error);
            archiveGrid.innerHTML = `<p class="text-red-500 text-center col-span-full p-5">Error loading archive: ${error.message}</p>`;
        }
    }

    if (typeof marked === 'undefined') {
        console.warn("marked.js not immediately available. Markdown rendering in archive might be delayed or use fallback.");
    }
    fetchAndDisplayArchive();
});
