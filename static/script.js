const storyTreeDiv = document.getElementById('story-tree');
let currentData = null; // Store the last received data
let isFetching = false; // Prevent multiple fetches at once

/**
 * Renders a single node (scene) and its choices recursively.
 * @param {object} node - The scene node object.
 * @param {object} metadata - The metadata object.
 * @returns {string} - The HTML string for the node.
 */
function renderNode(node, metadata) {
    if (!node) return '';

    let html = '<li>';

    // Determine classes for the scene div
    let sceneClasses = 'scene';
    if (metadata.current_id === node.id) sceneClasses += ' processing';
    if (metadata.last_added_id === node.id) sceneClasses += ' added';

    html += `<div class="${sceneClasses}" data-id="${node.id}">`;
    html += `<span class="scene-text">${node.text}</span>`;

    // Render choices if they exist
    if (node.child_choices && node.child_choices.length > 0) {
        html += '<ul class="choice-list">';
        node.child_choices.forEach(choice => {
            let choiceClasses = 'choice';
            if (metadata.current_id === choice.id) choiceClasses += ' processing';

            html += `<li class="${choiceClasses}" data-id="${choice.id}">`;
            html += `<span class="choice-text">➡️ ${choice.text}</span>`;

            // If a choice leads to another scene, render it recursively
            if (choice.child_scene) {
                html += '<ul>' + renderNode(choice.child_scene, metadata) + '</ul>';
            } else {
                // Mark as a leaf or if it's being processed
                html += ' <span class="leaf-marker">(Branch End)</span>';
                if (metadata.current_id === choice.id) {
                    html += ' <span class="processing-marker">(⚙️ Processing...)</span>';
                }
            }
            html += '</li>';
        });
        html += '</ul>';
    }

    html += '</div>';
    html += '</li>';
    return html;
}

/**
 * Fetches data from the backend and updates the UI.
 */
async function fetchData() {
    if (isFetching) return; // Skip if already fetching
    isFetching = true;

    try {
        const response = await fetch('/story_data');
        if (!response.ok) {
            storyTreeDiv.innerHTML = `Error: ${response.statusText}`;
            return;
        }
        const data = await response.json();

        // Handle errors or missing data from backend
        if (data.error) {
             // Keep showing the last known state or an error message
             if (!currentData) {
                storyTreeDiv.innerHTML = `Waiting for story_state.json... (${data.error})`;
             }
             return; // Don't update if there's an error/wait state
        }

        // Only update if data has changed (simple timestamp check)
        if (!currentData || (data.metadata && currentData.metadata && data.metadata.timestamp !== currentData.metadata.timestamp)) {
            currentData = data;
            if (data.story_tree) {
                // Start rendering from the root, wrapping in a top-level <ul>
                storyTreeDiv.innerHTML = `<ul>${renderNode(data.story_tree, data.metadata || {})}</ul>`;
            } else {
                storyTreeDiv.innerHTML = 'Waiting for story to start...';
            }
        }
    } catch (error) {
        console.error('Failed to fetch story data:', error);
        storyTreeDiv.innerHTML = 'Failed to load data. Is the backend running? Is story_state.json available?';
    } finally {
        isFetching = false; // Allow fetching again
    }
}

// Fetch data every 1.5 seconds
setInterval(fetchData, 1500);

// Initial fetch
fetchData();