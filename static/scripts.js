document.addEventListener('DOMContentLoaded', function () {
    loadStoredData();
    loadSubmissionHistory();

    document.getElementById('promptForm').addEventListener('submit', function (event) {
        event.preventDefault();
        submitFormData();
    });

    document.querySelectorAll('input, textarea').forEach(input => {
        input.addEventListener('input', () => {
            saveFormData();
            updatePrompt();
            updateConfigValues();
        });
    });
});

function saveFormData() {
    const data = collectFormData();

    fetch('/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).catch(error => console.error('Error saving data:', error));
}

function loadProfiles() {
    fetch('/profiles')
        .then(response => response.json())
        .then(profiles => {
            let profileSelect = document.getElementById("profileSelect");
            profileSelect.innerHTML = "";
            profiles.forEach(profile => {
                let option = document.createElement("option");
                option.value = profile;
                option.textContent = profile;
                profileSelect.appendChild(option);
            });
            loadProfile(profiles[0]);
        });
}

function loadProfile(profileName) {
    fetch('/profile/load', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile_name: profileName })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("name").value = data.name;
        document.getElementById("tone").value = data.tone;
        document.getElementById("interests").value = data.interests;
        document.getElementById("background").value = data.background;
        document.getElementById("mood").value = data.mood;
        document.getElementById("response_style").value = data.response_style;
        document.getElementById("preferences").value = data.preferences;
        document.getElementById("input_text").value = data.input_text;
        document.getElementById("profileImageDisplay").src = "/image/" + data.image;
    });
}
window.onload = loadProfiles;


function loadDefaultProfile() {
    fetch('/profile/load')
        .then(response => response.json())
        .then(profile => {
            document.getElementById("profileImageDisplay").src = profile.image;
        });
}

function switchProfile() {
    let selectedProfile = document.getElementById("profileSelect").value;
    fetch('/profile/load', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile_name: selectedProfile })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("name").value = data.name || "";
        document.getElementById("tone").value = data.tone || "";
        document.getElementById("interests").value = data.interests || "";
        document.getElementById("background").value = data.background || "";
        document.getElementById("mood").value = data.mood || "";
        document.getElementById("response_style").value = data.response_style || "";
        document.getElementById("preferences").value = data.preferences || "";
        document.getElementById("input_text").value = data.input_text || "";
        document.getElementById("temperature").value = data.temperature || 0.7;
        document.getElementById("max_length").value = data.max_length || 150;
        document.getElementById("top_k").value = data.top_k || 50;
        document.getElementById("top_p").value = data.top_p || 0.9;
        document.getElementById("repetition_penalty").value = data.repetition_penalty || 1.2;
        document.getElementById("num_return_sequences").value = data.num_return_sequences || 1;

        // Update model settings and prompt preview
        updateModelSettings();
        generatePromptPreview();

        // Update profile name and image
        document.getElementById("profileNameDisplay").innerText = data.name || "Profile Name";
        document.getElementById("profileImageDisplay").src = `/image/${data.image}`;
    })
    .catch(error => console.error('Error loading profile:', error));
}


// Update prompt preview in real-time
function generatePromptPreview() {
    let promptTemplate = `
<b>Assistant Profile:</b>
- <b>Name:</b> ${highlightText(document.getElementById("name").value)}
- <b>Background:</b> ${highlightText(document.getElementById("background").value)}
- <b>Tone:</b> ${highlightText(document.getElementById("tone").value)}
- <b>Interests:</b> ${highlightText(document.getElementById("interests").value)}
- <b>Response Style:</b> ${highlightText(document.getElementById("response_style").value)}
- <b>Mood:</b> ${highlightText(document.getElementById("mood").value)}

<b>Guidelines:</b>
- Answer user questions concisely and avoid repeating your profile information.
- Respond in a way that aligns with the given tone and response style.
- If you need to think, use <thinking>...</thinking> to indicate your thought process.

<b>User Input:</b> ${highlightText(document.getElementById("input_text").value)}
<b>Assistant:</b>
`;

    document.getElementById("generated_prompt").innerHTML = promptTemplate;
}

// Function to highlight non-empty fields
function highlightText(value) {
    return value.trim() !== "" ? `<span class="highlight">${value}</span>` : `(empty)`;
}




function updateModelSettings() {
    let modelSettings = `
    Temperature: ${document.getElementById("temperature").value}
    Max Length: ${document.getElementById("max_length").value}
    Top K: ${document.getElementById("top_k").value}
    Top P: ${document.getElementById("top_p").value}
    Repetition Penalty: ${document.getElementById("repetition_penalty").value}
    Number of Responses: ${document.getElementById("num_return_sequences").value}
    `;

    document.getElementById("model_settings").innerText = modelSettings;
}





document.getElementById("profileImage").addEventListener("change", function(event) {
    let file = event.target.files[0];
    let formData = new FormData();
    formData.append("image", file);

    fetch('/upload_image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("profileImageDisplay").src = "/image/" + data.filename;
    });
});

function saveProfile() {
    let profileName = document.getElementById("profileSelect").value;

    let profileData = {
        profile_name: profileName,
        name: document.getElementById("name").value,
        tone: document.getElementById("tone").value,
        interests: document.getElementById("interests").value,
        background: document.getElementById("background").value,
        mood: document.getElementById("mood").value,
        response_style: document.getElementById("response_style").value,
        preferences: document.getElementById("preferences").value,
        input_text: document.getElementById("input_text").value,
        temperature: parseFloat(document.getElementById("temperature").value),
        max_length: parseInt(document.getElementById("max_length").value),
        top_k: parseInt(document.getElementById("top_k").value),
        top_p: parseFloat(document.getElementById("top_p").value),
        repetition_penalty: parseFloat(document.getElementById("repetition_penalty").value),
        num_return_sequences: parseInt(document.getElementById("num_return_sequences").value),
        image: document.getElementById("profileImageDisplay").src.split('/').pop()
    };

    fetch('/profile/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileData)
    }).then(response => response.json())
    .then(data => alert(data.message))
    .catch(error => console.error('Error saving profile:', error));
}


window.onload = loadProfiles;

function createProfile() {
    let profileName = document.getElementById("newProfileName").value.trim();
    let profileImage = document.getElementById("profileImage").files[0];

    if (!profileName) {
        alert("Please enter a profile name.");
        return;
    }

    let formData = new FormData();
    formData.append("name", profileName);
    if (profileImage) {
        formData.append("image", profileImage);
    }

    fetch('/profile/create', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert(data.message);
            let profileSelect = document.getElementById("profileSelect");
            let newOption = document.createElement("option");
            newOption.value = profileName;
            newOption.textContent = profileName;
            profileSelect.appendChild(newOption);
            profileSelect.value = profileName;
            switchProfile();  // Load newly created profile

            // Hide input fields
            document.getElementById("newProfileName").style.display = 'none';
            document.getElementById("profileImage").style.display = 'none';
        }
    })
    .catch(error => console.error('Error creating profile:', error));
}




document.getElementById("profileImage").addEventListener("change", function(event) {
    let reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById("profileImageDisplay").src = e.target.result;
    }
    reader.readAsDataURL(event.target.files[0]);
});


function submitFormData() {
    const data = collectFormData();

    // Disable input fields and show processing message
    toggleFormInputs(true);
    displayPendingSubmission(data.input_text);

    fetch('/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        document.getElementById('ai_response').innerText = result.generated_response;
        updateHistory(result.generated_response, result.repeated, result.original_response);
    })
    .catch(error => console.error('Error submitting data:', error))
    .finally(() => {
        toggleFormInputs(false);
    });
}

function updateHistory(responseText, repeated, originalResponse) {
    const historyContainer = document.getElementById('submission_history');
    let responseDisplay = responseText;

    if (repeated) {
        responseDisplay = `<span class="highlight" onclick="toggleRepeatedResponse(this, '${escapeHtml(originalResponse)}')">${responseText} <button>[+]</button></span>`;
    }

    historyContainer.innerHTML = `
        <div class="submission">
            <strong>Input:</strong> ${document.getElementById('input_text').value}<br>
            <strong>Response:</strong> <span class="ai-response">${responseDisplay}</span><br>
            <small>${new Date().toLocaleString()}</small>
        </div><hr>` + historyContainer.innerHTML;
}


// Function to show pending input in history
function displayPendingSubmission(inputText) {
    const historyContainer = document.getElementById('submission_history');
    historyContainer.innerHTML = `
        <div class="submission pending">
            <strong>Input:</strong> ${inputText} <br>
            <strong>Status:</strong> Sending to AI...
        </div><hr>` + historyContainer.innerHTML;
}

// Function to enable/disable input fields during submission
function toggleFormInputs(disabled) {
    document.querySelectorAll('input, textarea, button').forEach(element => {
        element.disabled = disabled;
    });
}

function collectFormData() {
    return {
        name: document.getElementById('name').value,
        tone: document.getElementById('tone').value,
        interests: document.getElementById('interests').value,
        background: document.getElementById('background').value,
        mood: document.getElementById('mood').value,
        response_style: document.getElementById('response_style').value,
        preferences: document.getElementById('preferences').value,
        input_text: document.getElementById('input_text').value,
        temperature: parseFloat(document.getElementById('temperature').value),
        max_length: parseInt(document.getElementById('max_length').value),
        top_k: parseInt(document.getElementById('top_k').value),
        top_p: parseFloat(document.getElementById('top_p').value),
        repetition_penalty: parseFloat(document.getElementById('repetition_penalty').value),
        num_return_sequences: parseInt(document.getElementById('num_return_sequences').value)
    };
}

function loadStoredData() {
    fetch('/load')
    .then(response => response.json())
    .then(data => {
        for (let key in data) {
            if (document.getElementById(key)) {
                document.getElementById(key).value = data[key];
            }
        }
        updatePrompt();
        updateConfigValues();
    })
    .catch(error => console.error('Error loading data:', error));
}

document.addEventListener('DOMContentLoaded', function () {
    loadSubmissionHistory();
});

function loadSubmissionHistory() {
    fetch('/get_submissions')
        .then(response => response.json())
        .then(data => {
            const historyContainer = document.getElementById('submission_history');
            historyContainer.innerHTML = '';

            data.slice().reverse().forEach(entry => {  // Reverse the order
                let responseDisplay = entry.ai_response;

                historyContainer.innerHTML += `
                    <div class="submission">
                        <strong>Model Used:</strong> <span class="highlight">${entry.model_used}</span><br>
                        <strong>Input:</strong> ${entry.user_input.input_text} <br>
                        <strong>Response:</strong> <span class="ai-response">${responseDisplay}</span><br>
                        <small>${entry.timestamp}</small>
                    </div><hr>`;
            });

            addToggleFunctionality();
        })
        .catch(error => console.error('Error loading submissions:', error));
}


function updatePrompt() {
    const prompt = 
        `Assistant Profile:\n` +
        `- Name: <span class="highlight">${document.getElementById('name').value}</span>\n` +
        `- Tone: <span class="highlight">${document.getElementById('tone').value}</span>\n` +
        `- Interests: <span class="highlight">${document.getElementById('interests').value}</span>\n` +
        `- Background: <span class="highlight">${document.getElementById('background').value}</span>\n` +
        `- Mood: <span class="highlight">${document.getElementById('mood').value}</span>\n` +
        `- Response Style: <span class="highlight">${document.getElementById('response_style').value}</span>\n` +
        `- Preferences: <span class="highlight">${document.getElementById('preferences').value}</span>\n\n` +
        `Guidelines:\n` + 
        `- Answer user questions concisely and avoid repetition.\n` +
        `User: <span class="highlight">${document.getElementById('input_text').value}</span>\n<span">${document.getElementById('name').value}</span>:`;

    document.getElementById('generated_prompt').innerHTML = prompt;
}

// Function to update configuration display
function updateConfigValues() {
    const configDisplay = `
        Temperature: ${document.getElementById('temperature').value}<br>
        Max Length: ${document.getElementById('max_length').value}<br>
        Top K: ${document.getElementById('top_k').value}<br>
        Top P: ${document.getElementById('top_p').value}<br>
        Repetition Penalty: ${document.getElementById('repetition_penalty').value}<br>
        Number of Responses: ${document.getElementById('num_return_sequences').value}
    `;

    document.getElementById('model_settings').innerHTML = configDisplay;
}

// Function to toggle repeated response visibility
function addToggleFunctionality() {
    document.querySelectorAll('.highlight').forEach(element => {
        element.addEventListener('click', function () {
            if (this.dataset.expanded === "true") {
                this.innerHTML = " <-> ";
                this.dataset.expanded = "false";
            } else {
                this.innerHTML = escapeHtml(this.getAttribute("data-original"));
                this.dataset.expanded = "true";
            }
        });
    });
}

// Escape function to prevent HTML injection issues
function escapeHtml(str) {
    return str.replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")
              .replace(/"/g, "&quot;")
              .replace(/'/g, "&#039;");
}
document.addEventListener("DOMContentLoaded", function() {
    let inputs = document.querySelectorAll("#promptForm input, #promptForm textarea");
    inputs.forEach(input => {
        input.addEventListener("input", () => {
            saveProfileRealtime();
            generatePromptPreview();
        });
    });
});

function saveProfileRealtime() {
    let profileName = document.getElementById("profileSelect").value;

    let profileData = {
        profile_name: profileName,
        name: document.getElementById("name").value || "",
        tone: document.getElementById("tone").value || "",
        interests: document.getElementById("interests").value || "",
        background: document.getElementById("background").value || "",
        mood: document.getElementById("mood").value || "",
        response_style: document.getElementById("response_style").value || "",
        preferences: document.getElementById("preferences").value || "",
        input_text: document.getElementById("input_text").value || "",
        temperature: parseFloat(document.getElementById("temperature").value) || 0.7,
        max_length: parseInt(document.getElementById("max_length").value) || 150,
        top_k: parseInt(document.getElementById("top_k").value) || 50,
        top_p: parseFloat(document.getElementById("top_p").value) || 0.9,
        repetition_penalty: parseFloat(document.getElementById("repetition_penalty").value) || 1.2,
        num_return_sequences: parseInt(document.getElementById("num_return_sequences").value) || 1
    };

    fetch('/profile/update_realtime', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileData)
    })
    .then(response => response.json())
    .then(data => console.log("Profile auto-saved:", data.message))
    .catch(error => console.error('Error saving profile:', error));
}


document.addEventListener("DOMContentLoaded", function() {
    let inputs = document.querySelectorAll("#promptForm input, #promptForm textarea");
    inputs.forEach(input => {
        input.addEventListener("input", () => {
            saveProfileRealtime();
            generatePromptPreview();
            updateModelSettings();
        });
    });
});

document.addEventListener("DOMContentLoaded", function() {
    let inputs = document.querySelectorAll("#promptForm input, #promptForm textarea");
    inputs.forEach(input => {
        input.addEventListener("input", generatePromptPreview);
    });

    // Generate initial preview on load
    generatePromptPreview();
});
