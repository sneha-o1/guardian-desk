// helpdesk_mini/app.js

const API_BASE_URL = '/api/';
const appContent = document.getElementById('app-content');

let currentNextUrl = null;
let currentPrevUrl = null;

// --- Utility Functions ---

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getStatusClass(status) {
    switch (status) {
        case 'open':
            return 'badge-open';
        case 'in_progress':
            return 'badge-in_progress';
        case 'closed':
            return 'badge-closed';
        default:
            return 'bg-secondary';
    }
}

// --- DOM Rendering / Navigation ---

function renderListHtml(data) {
    return `
        <div class="alert alert-info border-0" role="alert">
             <i class="fa fa-info-circle me-2"></i>Status: Displaying tickets visible to your current access level.
        </div>
        <div class="row">
            <div class="col-md-4">
                <div class="card shadow-lg mb-4">
                    <div class="card-header bg-primary text-white"><h5 class="mb-0">Priority Input</h5></div>
                    <div class="card-body">
                        <form id="ticket-form">
                            <div class="mb-3">
                                <label for="title" class="form-label small">TITLE</label>
                                <input type="text" id="title" class="form-control" placeholder="Brief Summary" required>
                            </div>
                            <div class="mb-3">
                                <label for="description" class="form-label small">DETAILS</label>
                                <textarea id="description" class="form-control" placeholder="Full report required..." rows="5" required></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary w-100 mt-2">SUBMIT TICKET</button>
                        </form>
                    </div>
                </div>
            </div>

            <div class="col-md-8">
                <h5 class="text-light mb-3">TICKET LOG (<span id="ticket-count">${data.count || 0}</span> Total Records)</h5>
                <div id="tickets-container" class="mb-4">
                    ${data.results.map(renderTicketCard).join('')}
                </div>
                
                <div id="pagination-controls" class="d-flex justify-content-between">
                    <button id="prev-btn" class="btn btn-outline-secondary" disabled>Prev</button>
                    <button id="next-btn" class="btn btn-outline-secondary" disabled>Next</button>
                </div>
            </div>
        </div>
    `;
}

function renderTicketCard(ticket) {
    const statusClass = getStatusClass(ticket.status);
    const breachedTag = ticket.is_breached ? '<span class="badge badge-breached ms-2">BREACHED</span>' : '';
    const assigned = ticket.assigned_to ? ticket.assigned_to.username : 'UNASSIGNED';
    
    return `
        <div class="card mb-3 shadow-lg">
            <div class="card-header d-flex justify-content-between align-items-center ${statusClass}">
                <a href="#" onclick="showDetailPage(event, ${ticket.id})" class="btn-link-custom text-white">
                    <h6 class="mb-0">TICKET ${ticket.id} | ${ticket.title}</h6>
                </a>
                <div class="d-flex align-items-center">
                    <span class="badge ${statusClass} me-2">${ticket.status.toUpperCase()}</span>
                    ${breachedTag}
                </div>
            </div>
            <div class="card-body small">
                <p class="card-text text-muted">${ticket.description.substring(0, 150)}...</p>
                <div class="d-flex justify-content-between mt-2">
                    <span class="text-primary"><i class="fa fa-user me-1"></i>Owner: ${ticket.owner.username}</span>
                    <span class="text-secondary"><i class="fa fa-tag me-1"></i>Assigned: ${assigned}</span>
                </div>
            </div>
        </div>
    `;
}

async function showListPage(e) {
    if (e) e.preventDefault();
    appContent.innerHTML = '<p class="text-center text-muted py-5">Initiating secure connection...</p>';
    await fetchTickets(`${API_BASE_URL}tickets/`);
}

async function showDetailPage(e, ticketId) {
    if (e) e.preventDefault(); 
    appContent.innerHTML = '<p class="text-center text-muted">Loading Ticket Details...</p>';
    
    // 💥 FIX: Load HTML directly from the hidden template tag
    const template = document.getElementById('ticket-detail-template');
    const detailHtml = template.content.cloneNode(true);
    
    appContent.innerHTML = ''; // Clear the loading message
    appContent.appendChild(detailHtml); // Insert the structure
    
    // Continue fetching data and binding forms
    await fetchTicketDetails(ticketId);
    await fetchComments(ticketId);
    
    // Add event listeners for the forms on the new page
    document.getElementById('comment-form').addEventListener('submit', (e) => handleCommentSubmit(e, ticketId));
    document.getElementById('update-status-btn').addEventListener('click', (e) => handleStatusUpdate(e, ticketId));
    // NOTE: Assign button logic is not implemented, but the structure is there.
}

// --- API Calls (Same as before, adapted for new UI classes) ---

async function fetchTickets(url) {
    const response = await fetch(url);
    const data = await response.json();
    
    if (response.ok) {
        appContent.innerHTML = renderListHtml(data);
        updatePaginationControls(data.previous, data.next);
        document.getElementById('ticket-form').addEventListener('submit', handleSubmitTicket);
    } else {
         appContent.innerHTML = `<div class="alert alert-danger border-0 bg-dark text-white">
            <i class="fa fa-lock me-2"></i> ACCESS DENIED: Please authorize via the login button.
        </div>`;
    }
}

async function fetchTicketDetails(ticketId) {
    const response = await fetch(`${API_BASE_URL}tickets/${ticketId}/`);
    const ticket = await response.json();
    
    if (response.ok) {
        document.getElementById('detail-title').textContent = `#${ticket.id}: ${ticket.title}`;
        
        const statusEl = document.getElementById('detail-status');
        statusEl.textContent = ticket.status.toUpperCase();
        statusEl.className = `badge ${getStatusClass(ticket.status)} ms-3`;
        if (ticket.is_breached) statusEl.textContent += ' (BREACHED)';
        
        document.getElementById('detail-description').textContent = ticket.description;
        document.getElementById('detail-owner').innerHTML += ` ${ticket.owner.username}`;
        document.getElementById('detail-assigned').innerHTML += ` ${ticket.assigned_to ? ticket.assigned_to.username : 'N/A'}`;
        document.getElementById('detail-created').innerHTML += ` ${new Date(ticket.created_at).toLocaleString()}`;
        document.getElementById('detail-deadline').innerHTML += ` ${new Date(ticket.deadline).toLocaleDateString()}`;
        
        document.getElementById('action-status').value = ticket.status;
    } else {
        alert("Authorization failed to load ticket details.");
    }
}

// --- Form Handlers (CSRF token logic remains the same) ---

async function handleSubmitTicket(e) {
    e.preventDefault();

    const submitButton = e.target.querySelector('button[type="submit"]');
    submitButton.disabled = true;

    const headers = { 'Content-Type': 'application/json' };
    const csrftoken = getCookie('csrftoken');
    
    if (csrftoken) {
        headers['X-CSRFToken'] = csrftoken;
    } else {
        alert('Authorization Required: Please log in first via the Admin link.');
        submitButton.disabled = false;
        return;
    }

    const data = {
        title: document.getElementById('title').value,
        description: document.getElementById('description').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}tickets/`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert('Ticket submitted successfully! Initiating list refresh.');
            e.target.reset();
            await showListPage();
        } else {
            const error = await response.json();
            alert('Submission Failed. You must be authorized.');
        }
    } catch (error) {
        alert('Network Error. Ensure Django server is running.');
    } finally {
        submitButton.disabled = false;
    }
}

// ... include handleCommentSubmit, handleStatusUpdate, and updatePaginationControls functions here ...

async function handleCommentSubmit(e, ticketId) {
    e.preventDefault();
    const content = document.getElementById('comment-content').value;

    const headers = { 'Content-Type': 'application/json' };
    const csrftoken = getCookie('csrftoken');
    if (csrftoken) headers['X-CSRFToken'] = csrftoken;

    try {
        const response = await fetch(`${API_BASE_URL}tickets/${ticketId}/comments`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ content: content })
        });

        if (response.ok) {
            document.getElementById('comment-content').value = '';
            await fetchComments(ticketId);
        } else {
            alert('Comment failed. Are you logged in?');
        }
    } catch (error) {
        alert('Network error posting comment.');
    }
}

async function handleStatusUpdate(e, ticketId) {
    const newStatus = document.getElementById('action-status').value;
    
    const headers = { 'Content-Type': 'application/json' };
    const csrftoken = getCookie('csrftoken');
    if (csrftoken) headers['X-CSRFToken'] = csrftoken;

    try {
        const response = await fetch(`${API_BASE_URL}tickets/${ticketId}/`, {
            method: 'PATCH',
            headers: headers,
            body: JSON.stringify({ status: newStatus })
        });

        if (response.ok) {
            alert(`Status updated to ${newStatus}!`);
            showDetailPage(null, ticketId);
        } else {
             alert('Status update failed. Only Agents/Admins can change status.');
        }
    } catch (error) {
        alert('Network error updating status.');
    }
}

function updatePaginationControls(prevUrl, nextUrl) {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    
    prevBtn.disabled = !prevUrl;
    nextBtn.disabled = !nextUrl;

    prevBtn.onclick = () => { if (prevUrl) fetchTickets(prevUrl); };
    nextBtn.onclick = () => { if (nextUrl) fetchTickets(nextUrl); };
}

async function fetchComments(ticketId) {
    const response = await fetch(`${API_BASE_URL}tickets/${ticketId}/comments`);
    const commentsData = await response.json();
    const commentsContainer = document.getElementById('detail-comments');
    
    commentsContainer.innerHTML = '';

    if (commentsData.results && commentsData.results.length > 0) {
        commentsData.results.forEach(comment => {
            commentsContainer.innerHTML += `
                <div class="p-2 mb-2 bg-dark border border-secondary rounded">
                    <p class="mb-1">${comment.content}</p>
                    <footer class="blockquote-footer small text-muted">
                        <i class="fa fa-user me-1"></i> ${comment.user.username} at ${new Date(comment.created_at).toLocaleString()}
                    </footer>
                </div>
            `;
        });
    } else {
        commentsContainer.innerHTML = '<p class="text-muted small">No comments posted yet. Be the first to analyze this priority.</p>';
    }
}


// --- Initialization ---

document.addEventListener('DOMContentLoaded', () => {
    showListPage();
    
    // Fetch user info for Navbar
    fetch('/api/auth/user/')
        .then(res => res.json())
        .then(user => {
            const userInfo = document.getElementById('user-info');
            if (user.username) {
                userInfo.innerHTML = `<i class="fa fa-user me-1"></i> Access Level: ${user.role.toUpperCase()}`;
            }
        }).catch(() => { 
            // Already set to GUEST
        });
});