document.addEventListener('DOMContentLoaded', () => {
    const archiveGrid = document.getElementById('archiveGrid'); // Add ID to the grid container
    const homeButton = document.getElementById('homeLinkButton'); // Add ID to home button in header

    if (homeButton) {
        homeButton.addEventListener('click', (e) => {
            e.preventDefault(); // Prevent default anchor behavior
            window.location.href = '/'; // Navigate to home page (index.html)
        });
    }

    async function fetchAndDisplayArchive() {
        if (!archiveGrid) {
            console.error("Archive grid container not found.");
            return;
        }
        archiveGrid.innerHTML = '<p class="text-center col-span-full">Loading archived concepts...</p>';

        try {
            const response = await fetch('/api/archive');
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const concepts = await response.json();

            if (concepts.length === 0) {
                archiveGrid.innerHTML = '<p class="text-center col-span-full">No concepts have been archived yet.</p>';
                return;
            }

            archiveGrid.innerHTML = ''; // Clear loading message

            concepts.forEach(concept => {
                const conceptCard = document.createElement('div');
                conceptCard.className = 'flex flex-col gap-3 pb-3';

                // Image(s) - display first one if multiple
                let imagesHTML = '<div class="w-full bg-gray-200 aspect-video rounded-xl flex items-center justify-center"><p class="text-gray-500">No image</p></div>';
                if (concept.gemini_image_urls && concept.gemini_image_urls.length > 0) {
                    // For simplicity, we'll just show the first image.
                    // A more advanced version could have a carousel or show multiple thumbnails.
                    imagesHTML = `
                        <div
                          class="w-full bg-center bg-no-repeat aspect-video bg-cover rounded-xl"
                          style="background-image: url('${concept.gemini_image_urls[0]}');"
                          aria-label="Visualization for ${concept.prompt}"
                        ></div>`;
                }

                // Text content
                const textContentHTML = `
                    <div>
                        <p class="text-[#0d151c] text-base font-medium leading-normal truncate" title="${concept.prompt}">Prompt: ${concept.prompt}</p>
                        <p class="text-[#49749c] text-sm font-normal leading-normal line-clamp-3" title="${concept.flowise_response}">Concept: ${concept.flowise_response}</p>
                        <p class="text-gray-500 text-xs mt-1">Archived: ${new Date(concept.timestamp).toLocaleString()}</p>
                    </div>
                `;

                conceptCard.innerHTML = imagesHTML + textContentHTML;
                archiveGrid.appendChild(conceptCard);
            });

        } catch (error) {
            console.error("Error fetching archive:", error);
            archiveGrid.innerHTML = `<p class="text-red-500 text-center col-span-full">Error loading archive: ${error.message}</p>`;
        }
    }

    fetchAndDisplayArchive();
});
