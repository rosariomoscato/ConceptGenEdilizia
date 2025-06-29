document.addEventListener('DOMContentLoaded', () => {
    const generateButton = document.querySelector('button#generateConceptButton'); // Add ID to button
    const promptTextarea = document.querySelector('textarea[placeholder="Enter your concept prompt here..."]');
    const detailedConceptSection = document.getElementById('detailedConceptDesign'); // Add ID
    const generatedVisualizationsSection = document.getElementById('generatedVisualizations'); // Add ID
    const copyTextButton = document.getElementById('copyTextButton'); // Add ID
    const saveToArchiveButton = document.getElementById('saveToArchiveButton'); // Add ID
    const archiveButton = document.getElementById('archiveLinkButton'); // Add ID to header button

    let currentConceptData = null; // To store the latest generated concept

    if (archiveButton) {
        archiveButton.addEventListener('click', () => {
            window.location.href = '/archive.html'; // Navigate to archive page
        });
    }

    if (generateButton && promptTextarea) {
        generateButton.addEventListener('click', async () => {
            const prompt = promptTextarea.value.trim();
            if (!prompt) {
                alert("Please enter a concept prompt.");
                return;
            }

            // Show loading state
            detailedConceptSection.innerHTML = '<p class="text-center">Generating concept... Please wait.</p>';
            generatedVisualizationsSection.innerHTML = ''; // Clear previous images
            generateButton.disabled = true;
            generateButton.classList.add('opacity-50', 'cursor-not-allowed');

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ prompt: prompt }),
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                currentConceptData = data; // Store for archive and copy

                // Display Flowise text
                // detailedConceptSection.innerHTML = `<p class="text-[#101518] text-base font-normal leading-normal pb-3 pt-1 px-4">${data.flowise_response || "No text generated."}</p>`;

                // Display Flowise text (Rendered as Markdown)
                if (data.flowise_response) {
                    // Ensure the container has styles that make sense for markdown content.
                    // Tailwind's typography plugin would be great here, but for now, basic rendering.
                    detailedConceptSection.innerHTML = marked.parse(data.flowise_response);
                } else {
                    detailedConceptSection.innerHTML = '<p class="text-center">No text generated.</p>';
                }





                // Display Gemini images
                if (data.gemini_image_urls && data.gemini_image_urls.length > 0) {
                    const imageGrid = document.createElement('div');
                    imageGrid.className = 'grid grid-cols-[repeat(auto-fit,minmax(158px,1fr))] gap-3 p-4';
                    data.gemini_image_urls.forEach(imageUrl => {
                        const imgContainer = document.createElement('div');
                        imgContainer.className = 'flex flex-col gap-3';
                        const imgDiv = document.createElement('div');
                        imgDiv.className = 'w-full bg-center bg-no-repeat aspect-square bg-cover rounded-xl';
                        imgDiv.style.backgroundImage = `url('${imageUrl}')`;
                        imgContainer.appendChild(imgDiv);
                        imageGrid.appendChild(imgContainer);
                    });
                    generatedVisualizationsSection.appendChild(imageGrid);
                } else {
                    generatedVisualizationsSection.innerHTML = '<p class="text-center p-4">No visualizations generated.</p>';
                }
                // Enable Copy and Save buttons
                if(copyTextButton) copyTextButton.disabled = false;
                if(saveToArchiveButton) saveToArchiveButton.disabled = false;


            } catch (error) {
                console.error("Error generating concept:", error);
                detailedConceptSection.innerHTML = `<p class="text-red-500 text-center">Error: ${error.message}</p>`;
                generatedVisualizationsSection.innerHTML = '';
                 if(copyTextButton) copyTextButton.disabled = true;
                if(saveToArchiveButton) saveToArchiveButton.disabled = true;
            } finally {
                generateButton.disabled = false;
                generateButton.classList.remove('opacity-50', 'cursor-not-allowed');
            }
        });
    }

    if (copyTextButton) {
        copyTextButton.disabled = true; // Initially disabled
        copyTextButton.addEventListener('click', () => {
            if (currentConceptData && currentConceptData.flowise_response) {
                navigator.clipboard.writeText(currentConceptData.flowise_response)
                    .then(() => alert("Concept text copied to clipboard!"))
                    .catch(err => {
                        console.error("Failed to copy text: ", err);
                        alert("Failed to copy text. Please try again.");
                    });
            } else {
                alert("No concept text available to copy.");
            }
        });
    }

    if (saveToArchiveButton) {
        saveToArchiveButton.disabled = true; // Initially disabled
        saveToArchiveButton.addEventListener('click', async () => {
            if (!currentConceptData) {
                alert("No concept data to save. Please generate a concept first.");
                return;
            }

            saveToArchiveButton.disabled = true;
            saveToArchiveButton.classList.add('opacity-50');

            try {
                const response = await fetch('/api/archive', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(currentConceptData),
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                }
                alert("Concept saved to archive!");
            } catch (error) {
                console.error("Error saving to archive:", error);
                alert(`Error saving to archive: ${error.message}`);
            } finally {
                // Keep it disabled or re-enable based on desired UX
                // For now, let's re-enable if user wants to save again (e.g. after modification if that feature is added)
                 saveToArchiveButton.disabled = false; 
                 saveToArchiveButton.classList.remove('opacity-50');
            }
        });
    }
});
