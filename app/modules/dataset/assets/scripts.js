var currentId = 0;
        var amount_authors = 0;

        function show_upload_dataset() {
            document.getElementById("upload_dataset").style.display = "block";
        }

        function generateIncrementalId() {
            return currentId++;
        }

        function addField(newAuthor, name, text, className = 'col-lg-6 col-12 mb-3') {
            let fieldWrapper = document.createElement('div');
            fieldWrapper.className = className;

            let label = document.createElement('label');
            label.className = 'form-label';
            label.for = name;
            label.textContent = text;

            let field = document.createElement('input');
            field.name = name;
            field.className = 'form-control';

            fieldWrapper.appendChild(label);
            fieldWrapper.appendChild(field);
            newAuthor.appendChild(fieldWrapper);
        }

        function addRemoveButton(newAuthor) {
            let buttonWrapper = document.createElement('div');
            buttonWrapper.className = 'col-12 mb-2';

            let button = document.createElement('button');
            button.textContent = 'Remove author';
            button.className = 'btn btn-danger btn-sm';
            button.type = 'button';
            button.addEventListener('click', function (event) {
                event.preventDefault();
                newAuthor.remove();
            });

            buttonWrapper.appendChild(button);
            newAuthor.appendChild(buttonWrapper);
        }

        function createAuthorBlock(idx, suffix) {
            let newAuthor = document.createElement('div');
            newAuthor.className = 'author row';
            newAuthor.style.cssText = "border:2px dotted #ccc;border-radius:10px;padding:10px;margin:10px 0; background-color: white";

            addField(newAuthor, `${suffix}authors-${idx}-name`, 'Name *');
            addField(newAuthor, `${suffix}authors-${idx}-affiliation`, 'Affiliation');
            addField(newAuthor, `${suffix}authors-${idx}-orcid`, 'ORCID');
            addRemoveButton(newAuthor);

            return newAuthor;
        }

        function check_title_and_description() {
            let titleInput = document.querySelector('input[name="title"]');
            let descriptionTextarea = document.querySelector('textarea[name="desc"]');

            titleInput.classList.remove("error");
            descriptionTextarea.classList.remove("error");
            clean_upload_errors();

            let titleLength = titleInput.value.trim().length;
            let descriptionLength = descriptionTextarea.value.trim().length;

            if (titleLength < 3) {
                write_upload_error("title must be of minimum length 3");
                titleInput.classList.add("error");
            }

            if (descriptionLength < 3) {
                write_upload_error("description must be of minimum length 3");
                descriptionTextarea.classList.add("error");
            }

            return (titleLength >= 3 && descriptionLength >= 3);
        }


        document.getElementById('add_author').addEventListener('click', function () {
            let authors = document.getElementById('authors');
            let newAuthor = createAuthorBlock(amount_authors++, "");
            authors.appendChild(newAuthor);
        });


        document.addEventListener('click', function (event) {
            if (event.target && event.target.classList.contains('add_author_to_uvl')) {

                let authorsButtonId = event.target.id;
                let authorsId = authorsButtonId.replace("_button", "");
                let authors = document.getElementById(authorsId);
                let id = authorsId.replace("_form_authors", "")
                let newAuthor = createAuthorBlock(amount_authors, `feature_models-${id}-`);
                authors.appendChild(newAuthor);

            }
        });

        function show_loading() {
            document.getElementById("upload_button").style.display = "none";
            document.getElementById("loading").style.display = "block";
        }

        function hide_loading() {
            document.getElementById("upload_button").style.display = "block";
            document.getElementById("loading").style.display = "none";
        }

        function clean_upload_errors() {
            let upload_error = document.getElementById("upload_error");
            upload_error.innerHTML = "";
            upload_error.style.display = 'none';
        }

        function write_upload_error(error_message) {
            let upload_error = document.getElementById("upload_error");
            let alert = document.createElement('p');
            alert.style.margin = '0';
            alert.style.padding = '0';
            alert.textContent = 'Upload error: ' + error_message;
            upload_error.appendChild(alert);
            upload_error.style.display = 'block';
        }

        window.onload = function () {

            test_zenodo_connection();

            document.getElementById('upload_button').addEventListener('click', function () {

                clean_upload_errors();
                show_loading();

                // check title and description
                let check = check_title_and_description();

                if (check) {
                    // process data form
                    const formData = {};

                    ["basic_info_form", "uploaded_models_form"].forEach((formId) => {
                        const form = document.getElementById(formId);
                        const inputs = form.querySelectorAll('input, select, textarea');
                        inputs.forEach(input => {
                            if (input.name) {
                                formData[input.name] = formData[input.name] || [];
                                formData[input.name].push(input.value);
                            }
                        });
                    });

                    let formDataJson = JSON.stringify(formData);
                    console.log(formDataJson);

                    const csrfToken = document.getElementById('csrf_token').value;
                    const formUploadData = new FormData();
                    formUploadData.append('csrf_token', csrfToken);

                    for (let key in formData) {
                        if (formData.hasOwnProperty(key)) {
                            formUploadData.set(key, formData[key]);
                        }
                    }

                    let checked_orcid = true;
                    if (Array.isArray(formData.author_orcid)) {
                        for (let orcid of formData.author_orcid) {
                            orcid = orcid.trim();
                            if (orcid !== '' && !isValidOrcid(orcid)) {
                                hide_loading();
                                write_upload_error("ORCID value does not conform to valid format: " + orcid);
                                checked_orcid = false;
                                break;
                            }
                        }
                    }


                    let checked_name = true;
                    if (Array.isArray(formData.author_name)) {
                        for (let name of formData.author_name) {
                            name = name.trim();
                            if (name === '') {
                                hide_loading();
                                write_upload_error("The author's name cannot be empty");
                                checked_name = false;
                                break;
                            }
                        }
                    }


                    if (checked_orcid && checked_name) {
                        fetch('/dataset/upload', {
                            method: 'POST',
                            body: formUploadData
                        })
                            .then(response => {
                                if (response.ok) {
                                    console.log('Dataset sent successfully');
                                    response.json().then(data => {
                                        console.log(data.message);
                                        window.location.href = "/dataset/list";
                                    });
                                } else {
                                    response.json().then(data => {
                                        console.error('Error: ' + data.message);
                                        hide_loading();

                                        write_upload_error(data.message);

                                    });
                                }
                            })
                            .catch(error => {
                                console.error('Error in POST request:', error);
                            });
                    }


                } else {
                    hide_loading();
                }


            });
        };


        function isValidOrcid(orcid) {
            let orcidRegex = /^\d{4}-\d{4}-\d{4}-\d{4}$/;
            return orcidRegex.test(orcid);
        }

function showAlert(container, message, type) {
    if (!container) return;

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    container.innerHTML = '';
    container.appendChild(alertDiv);
}

function displayImportedFiles(source, files) {
    const fileList = document.getElementById('file-list');
    if (!fileList) {
        console.warn('file-list container not found');
        return;
    }

    files.forEach(filename => {
        const fileId = generateIncrementalId();

        const listItem = document.createElement('li');
        const h4Element = document.createElement('h4');
        h4Element.textContent = filename;
        listItem.appendChild(h4Element);

        // Info button
        const formButton = document.createElement('button');
        formButton.innerHTML = 'Show info';
        formButton.classList.add('info-button', 'btn', 'btn-outline-secondary', 'btn-sm');
        formButton.style.borderRadius = '5px';
        formButton.id = fileId + "_button";

        // Form container 
        const formContainer = document.createElement('div');
        formContainer.id = fileId + "_form";
        formContainer.classList.add('uvl_form', 'mt-3');
        formContainer.style.display = "none";

        formButton.addEventListener('click', function() {
            if (formContainer.style.display === "none") {
                formContainer.style.display = "block";
                formButton.innerHTML = 'Hide info';
            } else {
                formContainer.style.display = "none";
                formButton.innerHTML = 'Add info';
            }
        });

        // Space
        listItem.appendChild(document.createTextNode(" "));

        // Remove button
        const removeButton = document.createElement('button');
        removeButton.innerHTML = 'Delete model';
        removeButton.classList.add('remove-button', 'btn', 'btn-outline-danger', 'btn-sm');
        removeButton.style.borderRadius = '5px';

        removeButton.addEventListener('click', function() {
            // Remove from DOM
            fileList.removeChild(listItem);

            // Delete from server
            fetch('/dataset/file/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file: filename })
            });

            // Hide upload button if no files left
            if (fileList.children.length === 0) {
                document.getElementById("upload_dataset").style.display = "none";
                clean_upload_errors();
            }
        });

        listItem.appendChild(document.createTextNode(" "));
        listItem.appendChild(formButton);
        listItem.appendChild(removeButton);

        // UVL form 
        formContainer.innerHTML = `
            <div class="row">
                <input type="hidden" value="${filename}" name="feature_models-${fileId}-uvl_filename">
                <div class="col-12">
                    <div class="row">
                        <div class="col-12">
                            <div class="mb-3">
                                <label class="form-label">Title</label>
                                <input type="text" class="form-control" name="feature_models-${fileId}-title">
                            </div>
                        </div>
                        <div class="col-12">
                            <div class="mb-3">
                                <label class="form-label">Description</label>
                                <textarea rows="4" class="form-control" name="feature_models-${fileId}-desc"></textarea>
                            </div>
                        </div>
                        <div class="col-lg-6 col-12">
                            <div class="mb-3">
                                <label class="form-label">Publication type</label>
                                <select class="form-control" name="feature_models-${fileId}-publication_type">
                                    <option value="none">None</option>
                                    <option value="annotationcollection">Annotation Collection</option>
                                    <option value="book">Book</option>
                                    <option value="section">Book Section</option>
                                    <option value="conferencepaper">Conference Paper</option>
                                    <option value="datamanagementplan">Data Management Plan</option>
                                    <option value="article">Journal Article</option>
                                    <option value="patent">Patent</option>
                                    <option value="preprint">Preprint</option>
                                    <option value="deliverable">Project Deliverable</option>
                                    <option value="milestone">Project Milestone</option>
                                    <option value="proposal">Proposal</option>
                                    <option value="report">Report</option>
                                    <option value="softwaredocumentation">Software Documentation</option>
                                    <option value="taxonomictreatment">Taxonomic Treatment</option>
                                    <option value="technicalnote">Technical Note</option>
                                    <option value="thesis">Thesis</option>
                                    <option value="workingpaper">Working Paper</option>
                                    <option value="other">Other</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-lg-6 col-6">
                            <div class="mb-3">
                                <label class="form-label">Publication DOI</label>
                                <input class="form-control" name="feature_models-${fileId}-publication_doi" type="text">
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="mb-3">
                                <label class="form-label">Tags (separated by commas)</label>
                                <input type="text" class="form-control" name="feature_models-${fileId}-tags">
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="mb-3">
                                <label class="form-label">UVL version</label>
                                <input type="text" class="form-control" name="feature_models-${fileId}-uvl_version">
                            </div>
                        </div>
                        <div class="col-12">
                            <div class="mb-3">
                                <label class="form-label">Authors</label>
                                <div id="${formContainer.id}_authors"></div>
                                <button type="button" class="add_author_to_uvl btn btn-secondary" id="${formContainer.id}_authors_button">Add author</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        listItem.appendChild(formContainer);
        fileList.appendChild(listItem);
    });

    if (typeof feather !== 'undefined') {
        feather.replace();
    }

    show_upload_dataset();
}

// ========================================
// IMPORT FROM GITHUB
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const githubBtn = document.getElementById('import_github_btn');

    if (githubBtn) {
        githubBtn.addEventListener('click', function() {
            const githubUrlInput = document.getElementById('github_url');
            const githubUrl = githubUrlInput ? githubUrlInput.value.trim() : '';

            // Find or create alerts container
            let alertsContainer = document.getElementById('github-alerts');
            if (!alertsContainer) {
                alertsContainer = document.createElement('div');
                alertsContainer.id = 'github-alerts';
                alertsContainer.className = 'mt-3';
                const cardBody = githubBtn.closest('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(alertsContainer, cardBody.firstChild);
                }
            }

            // Basic validation
            if (!githubUrl) {
                showAlert(alertsContainer, 'Please enter a GitHub URL', 'danger');
                return;
            }

            if (!githubUrl.includes('github.com')) {
                showAlert(alertsContainer, 'Invalid GitHub URL', 'danger');
                return;
            }

            // Disable button and show loading
            const originalHTML = githubBtn.innerHTML;
            githubBtn.disabled = true;
            githubBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Importing...';

            // Clear previous alerts
            alertsContainer.innerHTML = '';

            // Call the import endpoint
            fetch('/dataset/import', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ github_url: githubUrl })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => Promise.reject(err));
                }
                return response.json();
            })
            .then(data => {
                githubBtn.disabled = false;
                githubBtn.innerHTML = originalHTML;

                if (typeof feather !== 'undefined') {
                    feather.replace();
                }

                if (data.files && data.files.length > 0) {
                    showAlert(alertsContainer,
                        `Successfully imported ${data.count} UVL file(s) from GitHub`,
                        'success'
                    );

                    // Display imported files
                    displayImportedFiles('github', data.files);

                    // Clear the input
                    if (githubUrlInput) {
                        githubUrlInput.value = '';
                    }

                    // Show upload dataset button
                    show_upload_dataset();
                } else {
                    showAlert(alertsContainer, data.message || 'No files imported', 'warning');
                }
            })
            .catch(error => {
                githubBtn.disabled = false;
                githubBtn.innerHTML = originalHTML;

                if (typeof feather !== 'undefined') {
                    feather.replace();
                }

                const errorMsg = error.message || 'Failed to import from GitHub';
                showAlert(alertsContainer, errorMsg, 'danger');
            });
        });
    }
});


// ========================================
// IMPORT FROM ZIP
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const zipBtn = document.getElementById('import_zip_btn');

    if (zipBtn) {
        zipBtn.addEventListener('click', function() {
            const zipFileInput = document.getElementById('zip_file');

            // Find or create alerts container
            let alertsContainer = document.getElementById('zip-alerts');
            if (!alertsContainer) {
                alertsContainer = document.createElement('div');
                alertsContainer.id = 'zip-alerts';
                alertsContainer.className = 'mt-3';
                const cardBody = zipBtn.closest('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(alertsContainer, cardBody.firstChild);
                }
            }

            // Basic validation
            if (!zipFileInput || !zipFileInput.files || zipFileInput.files.length === 0) {
                showAlert(alertsContainer, 'Please select a ZIP file', 'danger');
                return;
            }

            const file = zipFileInput.files[0];

            if (!file.name.toLowerCase().endsWith('.zip')) {
                showAlert(alertsContainer, 'Only ZIP files are allowed', 'danger');
                return;
            }

            // Disable button and show loading
            const originalHTML = zipBtn.innerHTML;
            zipBtn.disabled = true;
            zipBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Importing...';

            // Clear previous alerts
            alertsContainer.innerHTML = '';

            // Prepare form data
            const formData = new FormData();
            formData.append('file', file);

            // Call the import endpoint
            fetch('/dataset/import', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => Promise.reject(err));
                }
                return response.json();
            })
            .then(data => {
                zipBtn.disabled = false;
                zipBtn.innerHTML = originalHTML;

                if (typeof feather !== 'undefined') {
                    feather.replace();
                }

                if (data.files && data.files.length > 0) {
                    showAlert(alertsContainer,
                        `Successfully imported ${data.count} UVL file(s) from ZIP`,
                        'success'
                    );

                    // Display imported files
                    displayImportedFiles('zip', data.files);

                    // Clear the file input
                    zipFileInput.value = '';

                    // Show upload dataset button
                    show_upload_dataset();
                } else {
                    showAlert(alertsContainer, data.message || 'No files imported', 'warning');
                }
            })
            .catch(error => {
                zipBtn.disabled = false;
                zipBtn.innerHTML = originalHTML;

                if (typeof feather !== 'undefined') {
                    feather.replace();
                }

                const errorMsg = error.message || 'Failed to import from ZIP';
                showAlert(alertsContainer, errorMsg, 'danger');
            });
        });
    }
});