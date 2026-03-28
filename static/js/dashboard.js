/* ============================================
   Elite Wealth Capital - DASHBOARD JS
   Django backend version - server-rendered data
   ============================================ */

// Dashboard state
let dashboardRefreshInterval = null;
const DASHBOARD_REFRESH = 30000; // 30 seconds

// ==================== STATS ANIMATION ====================

// Animate stats cards on load
function animateStatsUpdate() {
    document.querySelectorAll('.stat-value').forEach(el => {
        el.classList.add('updated');
        setTimeout(() => el.classList.remove('updated'), 500);
    });
}

// ==================== NOTIFICATIONS ====================

// Toggle Notifications Dropdown
function toggleNotifications() {
    const dropdown = document.getElementById('notifDropdown');
    if (dropdown) {
        const isHidden = dropdown.style.display === 'none' || dropdown.style.display === '';
        dropdown.style.display = isHidden ? 'block' : 'none';

        if (isHidden && typeof playSound === 'function') {
            playSound('notification');
        }
    }
}

// Update Notification Badge
function updateNotificationBadge(count) {
    const badge = document.getElementById('notifCount');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
}

// ==================== REFERRAL CODE FUNCTIONS ====================

// Copy referral code to clipboard
function copyReferralCode() {
    const codeEl = document.getElementById('referralCode');
    const code = codeEl ? codeEl.textContent.trim() : '';

    if (!code) {
        alert('No referral code available');
        return;
    }

    navigator.clipboard.writeText(code).then(() => {
        const copyIcon = document.getElementById('copyIcon');
        if (copyIcon) {
            copyIcon.textContent = '✅';
            setTimeout(() => { copyIcon.textContent = '📋'; }, 2000);
        }
    }).catch(() => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = code;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
    });
}

// Share referral via various platforms
function shareReferral(platform) {
    const codeEl = document.getElementById('referralCode');
    const code = codeEl ? codeEl.textContent.trim() : '';

    if (!code) {
        alert('No referral code available');
        return;
    }

    const signupUrl = `${window.location.origin}/signup?ref=${code}`;
    const message = `Join Elite Wealth Capital using my referral code ${code} and get a $20 signup bonus! ${signupUrl}`;

    let shareUrl = '';
    switch (platform) {
        case 'whatsapp':
            shareUrl = `https://wa.me/?text=${encodeURIComponent(message)}`;
            break;
        case 'twitter':
            shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(message)}`;
            break;
        case 'email':
            shareUrl = `mailto:?subject=${encodeURIComponent('Join Elite Wealth Capital - $20 Bonus!')}&body=${encodeURIComponent(message)}`;
            break;
    }

    if (shareUrl) {
        window.open(shareUrl, '_blank');
    }
}

// Copy Referral Link (for a dedicated input element with id="referralLink")
function copyReferralLink() {
    const input = document.getElementById('referralLink');
    if (input) {
        input.select();
        navigator.clipboard.writeText(input.value).catch(() => {
            document.execCommand('copy');
        });
    }
}

// ==================== FORMAT HELPERS ====================

// Format Currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(amount);
}

// Format Time Ago
function formatTimeAgo(date) {
    const seconds = Math.floor((new Date() - new Date(date)) / 1000);
    const intervals = [
        { label: 'year', seconds: 31536000 },
        { label: 'month', seconds: 2592000 },
        { label: 'day', seconds: 86400 },
        { label: 'hour', seconds: 3600 },
        { label: 'minute', seconds: 60 }
    ];

    for (const interval of intervals) {
        const count = Math.floor(seconds / interval.seconds);
        if (count >= 1) {
            return `${count} ${interval.label}${count > 1 ? 's' : ''} ago`;
        }
    }
    return 'Just now';
}

// ==================== SIDEBAR & NAVIGATION ====================

function initSidebar() {
    const toggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        });

        if (localStorage.getItem('sidebarCollapsed') === 'true') {
            sidebar.classList.add('collapsed');
        }
    }

    // Highlight current page in sidebar based on current URL path
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-link, .mobile-drawer-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath === href) {
            link.classList.add('active');
        } else if (href && href !== '/' && currentPath.startsWith(href)) {
            link.classList.add('active');
        }
    });
}

// ==================== QUICK ACTIONS ====================

function quickInvest(planId) {
    window.location.href = planId ? `/invest/?plan=${planId}` : '/invest/';
}

function quickWithdraw() {
    window.location.href = '/withdraw/';
}

function quickAddFunds() {
    window.location.href = '/add-funds/';
}

// ==================== INITIALIZATION ====================

function initDashboard() {
    animateStatsUpdate();
    initSidebar();
    initVerticalTicker();

    const copyBtn = document.getElementById('copyReferralBtn');
    if (copyBtn) {
        copyBtn.addEventListener('click', copyReferralLink);
    }
}

// ==================== VERTICAL SIDEBAR TICKER ====================

async function initVerticalTicker() {
    const container = document.getElementById('tickerContent');
    if (!container) return;

    const coins = [
        { symbol: 'BTCUSDT',  name: 'BTC',  icon: '₿' },
        { symbol: 'ETHUSDT',  name: 'ETH',  icon: 'Ξ' },
        { symbol: 'BNBUSDT',  name: 'BNB',  icon: '⬡' },
        { symbol: 'SOLUSDT',  name: 'SOL',  icon: '◎' },
        { symbol: 'XRPUSDT',  name: 'XRP',  icon: '✕' },
        { symbol: 'ADAUSDT',  name: 'ADA',  icon: '₳' },
        { symbol: 'DOGEUSDT', name: 'DOGE', icon: 'Ð' },
        { symbol: 'TRXUSDT',  name: 'TRX',  icon: '◈' },
    ];

    // Fallback prices if API unreachable
    const fallback = {
        BTCUSDT:  { price: 84000,   change:  1.25 },
        ETHUSDT:  { price: 2000,    change: -0.85 },
        BNBUSDT:  { price: 580,     change:  0.92 },
        SOLUSDT:  { price: 135,     change:  2.15 },
        XRPUSDT:  { price: 2.20,    change:  1.35 },
        ADAUSDT:  { price: 0.72,    change: -0.45 },
        DOGEUSDT: { price: 0.18,    change:  3.20 },
        TRXUSDT:  { price: 0.24,    change:  0.50 },
    };

    let bybitMap = {};
    try {
        const resp = await fetch('https://api.bybit.com/v5/market/tickers?category=spot');
        if (resp.ok) {
            const json = await resp.json();
            if (json.retCode === 0 && json.result && json.result.list) {
                json.result.list.forEach(t => {
                    bybitMap[t.symbol] = {
                        price:  parseFloat(t.lastPrice),
                        change: parseFloat(t.price24hPcnt) * 100,
                    };
                });
            }
        }
    } catch (_) { /* use fallback */ }

    let html = '';
    coins.forEach(coin => {
        const d = bybitMap[coin.symbol] || fallback[coin.symbol];
        if (!d) return;
        const price = d.price < 1
            ? d.price.toFixed(4)
            : d.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        const changeFixed = d.change.toFixed(2);
        const isPos = d.change >= 0;
        html += `
        <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 12px;border-bottom:1px solid rgba(255,255,255,0.05);">
            <div style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:1.1rem;">${coin.icon}</span>
                <span style="color:#fff;font-weight:600;font-size:0.8rem;">${coin.name}</span>
            </div>
            <div style="text-align:right;">
                <div style="color:#FFD700;font-size:0.78rem;font-weight:600;">$${price}</div>
                <div style="color:${isPos ? '#00A86B' : '#EF4444'};font-size:0.7rem;">${isPos ? '+' : ''}${changeFixed}%</div>
            </div>
        </div>`;
    });

    container.innerHTML = html || '<p style="color:#94a3b8;padding:10px;font-size:0.8rem;">Loading…</p>';

    // Refresh every 60 seconds
    setTimeout(() => initVerticalTicker(), 60000);
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (dashboardRefreshInterval) {
        clearInterval(dashboardRefreshInterval);
    }
});

// Initialize on DOM Load
document.addEventListener('DOMContentLoaded', () => {
    if (document.body.classList.contains('dashboard-site')) {
        initDashboard();
    }
});

// Export functions for inline onclick handlers
window.copyReferralCode = copyReferralCode;
window.copyReferralLink = copyReferralLink;
window.shareReferral = shareReferral;
window.toggleNotifications = toggleNotifications;
window.formatCurrency = formatCurrency;
window.quickInvest = quickInvest;
window.quickWithdraw = quickWithdraw;
window.quickAddFunds = quickAddFunds;
