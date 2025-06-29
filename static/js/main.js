document.addEventListener('DOMContentLoaded', () => {
    const generateButton = document.querySelector('button#generateConceptButton');
    const promptTextarea = document.querySelector('textarea[placeholder="Enter your concept prompt here..."]');
    const detailedConceptSection = document.getElementById('detailedConceptDesign'); 
    const generatedVisualizationsSection = document.getElementById('generatedVisualizations');
    const copyTextButton = document.getElementById('copyTextButton'); 
    const saveToArchiveButton = document.getElementById('saveToArchiveButton'); 
    
    // Header links - using direct hrefs in HTML is simpler, so JS listeners for these are commented out.
    // const archiveLinkButton = document.getElementById('archiveLinkButtonIndex'); 
    // const helpLinkButton = document.getElementById('headerHelpLinkIndex');
    // if (archiveLinkButton) {
    //     archiveLinkButton.addEventListener('click', (e) => {
    //         e.preventDefault(); window.location.href = archiveLinkButton.href; 
    //     });
    // }
    // if (helpLinkButton) {
    //     helpLinkButton.addEventListener('click', (e) => {
    //         e.preventDefault(); window.location.href = helpLinkButton.href;
    //     });
    // }

    let currentConceptData = null; 

    if (generateButton && promptTextarea) {
        generateButton.addEventListener('click', async () => {
            const prompt = promptTextarea.value.trim();
            if (!prompt) {
                alert("Please enter a concept prompt.");
                return;
            }

            detailedConceptSection.innerHTML = '<p class="text-center p-4">Generating concept... Please wait.</p>';
            generatedVisualizationsSection.innerHTML = ''; 
            generateButton.disabled = true;
            generateButton.classList.add('opacity-50', 'cursor-not-allowed');
            if(copyTextButton) copyTextButton.disabled = true;
            if(saveToArchiveButton) saveToArchiveButton.disabled = true;


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
                    throw new Error(errorData.details || errorData.error || `HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                currentConceptData = data; 

                if (data.flowise_response && typeof marked !== 'undefined') {
                    detailedConceptSection.innerHTML = marked.parse(data.flowise_response);
                } else if (data.flowise_response) {
                    // Fallback if marked.js somehow isn't loaded but we have text
                    const p = document.createElement('p');
                    p.textContent = data.flowise_response;
                    detailedConceptSection.innerHTML = ''; // Clear previous
                    detailedConceptSection.appendChild(p);
                } else {
                    detailedConceptSection.innerHTML = '<p class="text-center p-4">No text generated.</p>';
                }

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
                
                if(copyTextButton) copyTextButton.disabled = false;
                if(saveToArchiveButton) saveToArchiveButton.disabled = false;

            } catch (error) {
                console.error("Error generating concept:", error);
                detailedConceptSection.innerHTML = `<p class="text-red-500 text-center p-4">Error: ${error.message}</p>`;
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
        copyTextButton.disabled = true; 
        copyTextButton.addEventListener('click', () => {
            if (currentConceptData && currentConceptData.flowise_response) {
                // If using marked.js, the raw markdown is in currentConceptData.flowise_response
                // The rendered HTML is in detailedConceptSection.innerHTML
                // For copying, usually the raw text (markdown) is preferred.
                navigator.clipboard.writeText(currentConceptData.flowise_response)
                    .then(() => alert("Concept text copied to clipboard!"))
                    .catch(err => {
                        console.error("Failed to copy text: ", err);
                        // Fallback for older browsers or if clipboard API fails
                        try {
                            const textArea = document.createElement("textarea");
                            textArea.value = currentConceptData.flowise_response;
                            document.body.appendChild(textArea);
                            textArea.focus();
                            textArea.select();
                            document.execCommand('copy');
                            document.body.removeChild(textArea);
                            alert("Concept text copied to clipboard (fallback method)!");
                        } catch (e) {
                            alert("Failed to copy text. Please try again or copy manually.");
                        }
                    });
            } else {
                alert("No concept text available to copy.");
            }
        });
    }

    if (saveToArchiveButton) {
        saveToArchiveButton.disabled = true; 
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
                 saveToArchiveButton.disabled = false; 
                 saveToArchiveButton.classList.remove('opacity-50');
            }
        });
    }
});