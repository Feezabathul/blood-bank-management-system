/*
    Sophisticated Client-Side Logic for BloodConnect
    Author: Antigravity AI
*/

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    const path = window.location.pathname;
    
    // Page routing
    if (path === '/' || path.endsWith('index.html')) {
        loadDashboard();
    } else if (path.includes('register')) {
        initRegisterForm();
    } else if (path.includes('donation')) {
        initDonationForm();
    } else if (path.includes('search')) {
        initSearchPage();
    } else if (path.includes('donors')) {
        loadDonorsTable();
    }

    // Active link highlighting fallback (if not handled by backend)
    document.querySelectorAll('.nav-links a').forEach(link => {
        if (link.getAttribute('href') === path) {
            link.classList.add('active');
        }
    });
}

// --- Premium Toast System ---
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? '✓' : '✕';
    
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background: ${type === 'success' ? 'var(--success)' : 'var(--error)'}; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold;">
                ${icon}
            </div>
            <span style="font-weight: 500;">${message}</span>
        </div>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;color:var(--text-muted);cursor:pointer;font-size:18px;">&times;</button>
    `;
    
    container.appendChild(toast);
    
    // Auto-remove
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(20px)';
        toast.style.transition = 'all 0.5s ease';
        setTimeout(() => toast.remove(), 500);
    }, 5000);
}

// --- API Wrapper ---
async function api(url, method = 'GET', body = null) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (body) options.body = JSON.stringify(body);

    try {
        const response = await fetch(url, options);
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Request failed');
        return data;
    } catch (err) {
        showToast(err.message, 'error');
        throw err;
    }
}

// --- Dashboard Logic ---
async function loadDashboard() {
    try {
        const stats = await api('/api/stats');
        
        // Counter Animation effect
        animateValue('stat-total_donors', 0, stats.total_donors, 1000);
        animateValue('stat-monthly_donations', 0, stats.monthly_donations, 1000);
        animateValue('stat-eligible_donors', 0, stats.eligible_donors, 1000);
        
        // Custom ID matches if they are different in HTML
        document.getElementById('stat-total-donors').textContent = stats.total_donors;
        document.getElementById('stat-monthly-donations').textContent = stats.monthly_donations;
        document.getElementById('stat-eligible-donors').textContent = stats.eligible_donors;

        // Blood Group Grid
        const grid = document.getElementById('blood-group-grid');
        const groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'];
        
        grid.innerHTML = groups.map(group => {
            const count = stats.blood_counts[group] || 0;
            return `
                <div class="stat-card" style="padding: 1.5rem; text-align: center; border-top: none; border: 1px solid #eee; display: flex; flex-direction: column; align-items: center;">
                    <div style="font-size: 1.2rem; font-weight: 800; color: var(--primary-red); margin-bottom: 0.5rem;">${group}</div>
                    <div style="font-size: 2rem; font-weight: 700;">${count}</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;">Donors</div>
                </div>
            `;
        }).join('');

    } catch (e) { console.error('Dashboard Error:', e); }
}

function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    if (!obj) return;
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// --- Registration Logic ---
function initRegisterForm() {
    const form = document.getElementById('register-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Advanced Validation
        const age = parseInt(form.age.value);
        if (age < 18 || age > 65) return showToast('Age must be between 18 and 65', 'error');
        
        const phone = form.contact.value;
        if (!/^\d{10}$/.test(phone)) return showToast('Phone must be exactly 10 digits', 'error');

        const data = {
            full_name: form.full_name.value,
            age: age,
            gender: form.gender.value,
            blood_group: form.blood_group.value,
            contact: phone,
            address: form.address.value
        };

        try {
            const btn = form.querySelector('button');
            const originalText = btn.textContent;
            btn.disabled = true;
            btn.textContent = 'Processing...';

            await api('/api/register', 'POST', data);
            showToast('Donor registered successfully!', 'success');
            form.reset();
            
            btn.disabled = false;
            btn.textContent = originalText;
        } catch (e) {
            form.querySelector('button').disabled = false;
            form.querySelector('button').textContent = 'Complete Registration';
        }
    });
}

// --- Donation Logic ---
async function initDonationForm() {
    const form = document.getElementById('donation-form');
    const select = document.getElementById('donor_id');
    if (!form) return;

    // Load donors
    try {
        const donors = await api('/api/donors');
        donors.sort((a, b) => a.full_name.localeCompare(b.full_name));
        donors.forEach(d => {
            const opt = document.createElement('option');
            opt.value = d.id;
            opt.textContent = `${d.full_name} (${d.blood_group}) - ID: ${d.id}`;
            select.appendChild(opt);
        });
    } catch (e) { }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const data = {
            donor_id: form.donor_id.value,
            donation_date: form.donation_date.value,
            units_donated: parseInt(form.units_donated.value)
        };

        try {
            const btn = form.querySelector('button');
            btn.disabled = true;
            btn.textContent = 'Logging Donation...';

            const res = await api('/api/donate', 'POST', data);
            showToast(res.message, 'success');
            form.reset();
            document.getElementById('donation_date').valueAsDate = new Date();
            
            btn.disabled = false;
            btn.textContent = 'Record Donation Entry';
        } catch (e) {
            form.querySelector('button').disabled = false;
            form.querySelector('button').textContent = 'Record Donation Entry';
        }
    });
}

// --- Search Logic ---
function initSearchPage() {
    const form = document.getElementById('search-form');
    const results = document.getElementById('search-results');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const bg = form.blood_group.value;
        
        try {
            results.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 2rem;">Searching database...</div>';
            const data = await api(`/api/search?blood_group=${encodeURIComponent(bg)}`);
            
            if (data.length === 0) {
                results.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 4rem; color: var(--text-muted);">No donors found for this blood group.</div>';
                return;
            }

            results.innerHTML = data.map(d => `
                <div class="donor-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                        <h3 style="color: var(--primary-dark);">${d.full_name}</h3>
                        <span class="badge ${d.eligible ? 'badge-success' : 'badge-error'}">${d.eligible ? 'Eligible' : 'Ineligible'}</span>
                    </div>
                    <div style="color: var(--text-muted); font-size: 0.95rem;">
                        <p><strong>Contact:</strong> ${d.contact}</p>
                        <p><strong>Last Donation:</strong> ${d.last_date}</p>
                        <p style="margin-top: 0.5rem; font-style: italic;">Group: ${d.blood_group}</p>
                    </div>
                </div>
            `).join('');
        } catch (e) { }
    });
}

// --- Donor List Logic ---
async function loadDonorsTable() {
    const tableBody = document.querySelector('#donor-list-table tbody');
    if (!tableBody) return;

    try {
        const donors = await api('/api/donors');
        if (donors.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 4rem;">No donors registered yet.</td></tr>';
            return;
        }

        tableBody.innerHTML = donors.map(d => `
            <tr>
                <td style="font-weight: 600;">#${d.id}</td>
                <td style="font-weight: 500;">${d.full_name}</td>
                <td><span style="color: var(--primary-red); font-weight: 700;">${d.blood_group}</span></td>
                <td>${d.age}</td>
                <td>${d.contact}</td>
                <td>${d.last_date}</td>
                <td><span class="badge ${d.eligible ? 'badge-success' : 'badge-error'}">${d.eligible ? 'Eligible' : 'Ineligible'}</span></td>
                <td>
                    <button onclick="deleteDonor(${d.id})" class="btn-delete" style="color: var(--error); background: none; border: none; cursor: pointer; font-weight: 600; padding: 5px;">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (e) { }
}

async function deleteDonor(id) {
    if (!confirm('This will permanently remove the donor and all their records. Proceed?')) return;
    
    try {
        await api(`/api/delete/${id}`, 'DELETE');
        showToast('Donor profile removed', 'success');
        loadDonorsTable();
    } catch (e) { }
}
