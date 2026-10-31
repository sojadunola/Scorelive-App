/**
 * ScorePulse - Frontend Application Logic
 */

let state = {
  leagues: [],
  currentLeague: 'eng.1',
  currentLeagueName: 'Premier League',
  currentLeagueIcon: '⚽',
  currentMode: 'auto', // 'auto' or 'sim'
  currentTab: 'all',   // 'all', 'live', 'pre', 'post', 'favorites'
  searchQuery: '',
  matches: [],
  filteredMatches: [],
  favorites: new Set(JSON.parse(localStorage.getItem('sp_favorites') || '[]')),
  audioEnabled: localStorage.getItem('sp_audio') === 'true',
  lastScores: {},
  countdown: 15,
  refreshInterval: null,
  activeModalMatch: null,
  activeModalTab: 'events'
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  loadLeagues();
  updateAudioIcon();
  startRefreshLoop();
});

function setupEventListeners() {
  const searchInput = document.getElementById('teamSearchInput');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value.toLowerCase().trim();
      applyFilters();
    });
  }
}

// Start Countdown and Auto-Refresh
function startRefreshLoop() {
  if (state.refreshInterval) clearInterval(state.refreshInterval);

  state.countdown = 15;
  updateCountdownDisplay();

  state.refreshInterval = setInterval(() => {
    state.countdown--;
    updateCountdownDisplay();
    if (state.countdown <= 0) {
      state.countdown = 15;
      fetchScores(false);
    }
  }, 1000);
}

function updateCountdownDisplay() {
  const el = document.getElementById('countdownText');
  if (el) el.textContent = `${state.countdown}s`;
}

// Audio notification
function toggleAudio() {
  state.audioEnabled = !state.audioEnabled;
  localStorage.setItem('sp_audio', state.audioEnabled);
  updateAudioIcon();
}

function updateAudioIcon() {
  const icon = document.getElementById('audioIcon');
  if (icon) {
    if (state.audioEnabled) {
      icon.className = 'ph-bold ph-speaker-simple-high text-emerald-400';
    } else {
      icon.className = 'ph-bold ph-speaker-simple-slash text-gray-500';
    }
  }
}

function playGoalSound() {
  if (!state.audioEnabled) return;
  const audio = document.getElementById('goalAudio');
  if (audio) {
    audio.currentTime = 0;
    audio.play().catch(e => console.log('Audio autoplay prevented:', e));
  }
}

// Mode Selection (Live ESPN vs Sim Engine)
function setMode(mode) {
  state.currentMode = mode;
  const autoBtn = document.getElementById('modeAutoBtn');
  const simBtn = document.getElementById('modeSimBtn');

  if (mode === 'auto') {
    autoBtn.className = 'px-2.5 py-1 rounded-md transition-all bg-blue-600 text-white shadow-sm';
    simBtn.className = 'px-2.5 py-1 rounded-md transition-all text-gray-400 hover:text-white';
  } else {
    simBtn.className = 'px-2.5 py-1 rounded-md transition-all bg-blue-600 text-white shadow-sm';
    autoBtn.className = 'px-2.5 py-1 rounded-md transition-all text-gray-400 hover:text-white';
  }

  fetchScores(true);
}

// Fetch supported leagues
async function loadLeagues() {
  try {
    const res = await fetch('/api/leagues');
    const data = await res.json();
    if (data.success) {
      state.leagues = data.leagues;
      renderLeagues();
      fetchScores(true);
      fetchStandings();
    }
  } catch (err) {
    console.error('Failed to load leagues:', err);
  }
}

function renderLeagues() {
  const container = document.getElementById('leaguePillsContainer');
  if (!container) return;

  container.innerHTML = state.leagues.map(l => {
    const isActive = l.id === state.currentLeague;
    return `
      <button 
        onclick="selectLeague('${l.id}', '${l.name}', '${l.icon}')"
        class="whitespace-nowrap px-3 py-1.5 rounded-full flex items-center space-x-1.5 transition-all text-xs font-semibold ${
          isActive 
            ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20' 
            : 'bg-gray-800/80 text-gray-300 hover:bg-gray-700/80 hover:text-white'
        }"
      >
        <span>${l.icon}</span>
        <span>${l.name}</span>
      </button>
    `;
  }).join('');
}

function selectLeague(id, name, icon) {
  state.currentLeague = id;
  state.currentLeagueName = name;
  state.currentLeagueIcon = icon;
  renderLeagues();
  document.getElementById('currentLeagueDisplay').textContent = name;
  document.getElementById('standingsLeagueTag').textContent = icon + ' ' + name;
  fetchScores(true);
  fetchStandings();
}

// Fetch Scores
async function fetchScores(showSpinner = false) {
  const spinner = document.getElementById('refreshSpinner');
  if (showSpinner && spinner) spinner.classList.add('animate-spin');

  try {
    const url = `/api/scores?league=${state.currentLeague}&mode=${state.currentMode}`;
    const res = await fetch(url);
    const result = await res.json();

    if (result.success && result.data) {
      const data = result.data;
      
      // Check for demo notice
      const simNotice = document.getElementById('simNotice');
      if (simNotice) {
        if (data.note || state.currentMode === 'sim' || data.source === 'simulation') {
          simNotice.classList.remove('hidden');
        } else {
          simNotice.classList.add('hidden');
        }
      }

      // Update provider badge
      const badge = document.getElementById('dataSourceBadge');
      if (badge) {
        badge.textContent = `Provider: ${data.source === 'simulation' ? 'Sim Engine' : 'ESPN Public'}`;
      }

      // Check for score change to play chime
      checkForGoalEvents(data.matches || []);

      state.matches = data.matches || [];
      updateCounts();
      applyFilters();
    }
  } catch (err) {
    console.error('Error fetching scores:', err);
  } finally {
    if (showSpinner && spinner) spinner.classList.remove('animate-spin');
  }
}

function checkForGoalEvents(newMatches) {
  let goalScored = false;
  newMatches.forEach(m => {
    const key = m.id;
    const currentScore = `${m.home.score}-${m.away.score}`;
    if (state.lastScores[key] && state.lastScores[key] !== currentScore) {
      // Score changed!
      goalScored = true;
    }
    state.lastScores[key] = currentScore;
  });

  if (goalScored) {
    playGoalSound();
  }
}

function updateCounts() {
  const all = state.matches.length;
  const live = state.matches.filter(m => m.is_live).length;
  const pre = state.matches.filter(m => m.state === 'pre').length;
  const post = state.matches.filter(m => m.is_finished).length;
  const fav = state.matches.filter(m => state.favorites.has(m.id)).length;

  document.getElementById('count-all').textContent = all;
  document.getElementById('count-live').textContent = live;
  document.getElementById('count-pre').textContent = pre;
  document.getElementById('count-post').textContent = post;
  document.getElementById('count-fav').textContent = fav;
}

function setTab(tab) {
  state.currentTab = tab;
  ['all', 'live', 'pre', 'post', 'favorites'].forEach(t => {
    const el = document.getElementById(`tab-${t}`);
    if (el) {
      if (t === tab) {
        el.className = 'px-3 py-1.5 rounded-lg transition-all bg-blue-600 text-white font-semibold';
      } else {
        el.className = 'px-3 py-1.5 rounded-lg transition-all text-gray-400 hover:text-white font-semibold';
      }
    }
  });
  applyFilters();
}

function toggleFavorite(id, event) {
  if (event) event.stopPropagation();
  if (state.favorites.has(id)) {
    state.favorites.delete(id);
  } else {
    state.favorites.add(id);
  }
  localStorage.setItem('sp_favorites', JSON.stringify(Array.from(state.favorites)));
  updateCounts();
  applyFilters();
}

function applyFilters() {
  let list = [...state.matches];

  // Tab filter
  if (state.currentTab === 'live') {
    list = list.filter(m => m.is_live);
  } else if (state.currentTab === 'pre') {
    list = list.filter(m => m.state === 'pre');
  } else if (state.currentTab === 'post') {
    list = list.filter(m => m.is_finished);
  } else if (state.currentTab === 'favorites') {
    list = list.filter(m => state.favorites.has(m.id));
  }

  // Search filter
  if (state.searchQuery) {
    list = list.filter(m => 
      m.home.name.toLowerCase().includes(state.searchQuery) ||
      m.away.name.toLowerCase().includes(state.searchQuery) ||
      m.league_name.toLowerCase().includes(state.searchQuery)
    );
  }

  // Sort pinned favorites to top
  list.sort((a, b) => {
    const aFav = state.favorites.has(a.id) ? 1 : 0;
    const bFav = state.favorites.has(b.id) ? 1 : 0;
    if (aFav !== bFav) return bFav - aFav;
    if (a.is_live && !b.is_live) return -1;
    if (!a.is_live && b.is_live) return 1;
    return 0;
  });

  state.filteredMatches = list;
  renderMatches();
}

function renderMatches() {
  const container = document.getElementById('matchesContainer');
  const emptyState = document.getElementById('emptyState');
  if (!container) return;

  if (state.filteredMatches.length === 0) {
    container.innerHTML = '';
    if (emptyState) emptyState.classList.remove('hidden');
    return;
  }

  if (emptyState) emptyState.classList.add('hidden');

  container.innerHTML = state.filteredMatches.map(m => {
    const isFav = state.favorites.has(m.id);
    const isLive = m.is_live;
    const isFinished = m.is_finished;

    // Status pill
    let statusBadge = '';
    if (isLive) {
      statusBadge = `
        <span class="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-red-500/10 text-red-400 border border-red-500/30">
          <span class="w-1.5 h-1.5 rounded-full bg-red-500 live-pulse"></span>
          <span>${m.clock || 'LIVE'}</span>
        </span>
      `;
    } else if (isFinished) {
      statusBadge = `
        <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-gray-800 text-gray-300">
          FT
        </span>
      `;
    } else {
      const matchTime = m.date ? new Date(m.date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Upcoming';
      statusBadge = `
        <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
          ${matchTime}
        </span>
      `;
    }

    return `
      <div 
        onclick="openMatchModal('${m.league_id}', '${m.id}')"
        class="match-card rounded-2xl p-4 sm:p-5 cursor-pointer relative group"
      >
        <!-- Top bar: League, Status, Favorite Star -->
        <div class="flex items-center justify-between pb-3 border-b border-gray-800/80 text-xs">
          <div class="flex items-center space-x-2 text-gray-400">
            <span>${m.league_icon || '⚽'}</span>
            <span class="font-medium text-gray-300">${m.league_name}</span>
            ${m.venue ? `<span class="hidden sm:inline text-gray-500">• ${m.venue}</span>` : ''}
          </div>
          <div class="flex items-center space-x-3">
            ${statusBadge}
            <button 
              onclick="toggleFavorite('${m.id}', event)" 
              title="Pin match"
              class="text-gray-500 hover:text-amber-400 transition-colors"
            >
              <i class="${isFav ? 'ph-fill ph-star text-amber-400' : 'ph ph-star'} text-lg"></i>
            </button>
          </div>
        </div>

        <!-- Center Teams and Scores -->
        <div class="grid grid-cols-12 items-center py-4">
          <!-- Home Team -->
          <div class="col-span-5 flex items-center space-x-3">
            <img 
              src="${m.home.logo || 'https://via.placeholder.com/48?text=Home'}" 
              alt="${m.home.name}" 
              onerror="this.src='https://via.placeholder.com/48?text=FC'"
              class="w-10 h-10 sm:w-12 sm:h-12 object-contain drop-shadow"
            >
            <div>
              <h4 class="font-bold text-sm sm:text-base text-gray-100 group-hover:text-blue-400 transition-colors line-clamp-1">
                ${m.home.name}
              </h4>
              <span class="text-[11px] text-gray-400 font-mono">${m.home.record || 'Home'}</span>
            </div>
          </div>

          <!-- Score Display -->
          <div class="col-span-2 flex flex-col items-center justify-center">
            ${isLive || isFinished ? `
              <div class="score-badge px-3 py-1 rounded-lg text-lg sm:text-2xl font-bold ${isLive ? 'text-emerald-400' : 'text-gray-200'}">
                ${m.home.score} - ${m.away.score}
              </div>
            ` : `
              <div class="text-xs font-semibold uppercase text-gray-400 bg-gray-900 px-2.5 py-1 rounded border border-gray-800">
                VS
              </div>
            `}
          </div>

          <!-- Away Team -->
          <div class="col-span-5 flex items-center justify-end space-x-3 text-right">
            <div>
              <h4 class="font-bold text-sm sm:text-base text-gray-100 group-hover:text-blue-400 transition-colors line-clamp-1">
                ${m.away.name}
              </h4>
              <span class="text-[11px] text-gray-400 font-mono">${m.away.record || 'Away'}</span>
            </div>
            <img 
              src="${m.away.logo || 'https://via.placeholder.com/48?text=Away'}" 
              alt="${m.away.name}" 
              onerror="this.src='https://via.placeholder.com/48?text=FC'"
              class="w-10 h-10 sm:w-12 sm:h-12 object-contain drop-shadow"
            >
          </div>
        </div>

        <!-- Footer / Broadcast & View Details -->
        <div class="flex items-center justify-between pt-2 text-[11px] text-gray-400">
          <div>
            ${m.headline ? `<span class="italic text-gray-400 line-clamp-1">${m.headline}</span>` : (m.broadcast ? `<span>📺 ${m.broadcast}</span>` : '')}
          </div>
          <div class="flex items-center space-x-1 text-blue-400 font-semibold group-hover:translate-x-1 transition-transform">
            <span>Match Centre</span>
            <i class="ph-bold ph-caret-right"></i>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// Standings
async function fetchStandings() {
  const container = document.getElementById('standingsRowsContainer');
  if (!container) return;

  try {
    const res = await fetch(`/api/standings/${state.currentLeague}`);
    const data = await res.json();
    if (data.success && data.standings) {
      renderStandings(data.standings);
    }
  } catch (err) {
    console.error('Failed to fetch standings:', err);
  }
}

function renderStandings(rows) {
  const container = document.getElementById('standingsRowsContainer');
  if (!container) return;

  if (!rows || rows.length === 0) {
    container.innerHTML = `<div class="text-xs text-gray-500 py-4 text-center">Standings not available for this league.</div>`;
    return;
  }

  container.innerHTML = rows.map((r, i) => {
    let rankColor = 'text-gray-400';
    if (r.rank <= 4) rankColor = 'text-blue-400 font-bold';
    if (r.rank >= rows.length - 2) rankColor = 'text-red-400 font-bold';

    return `
      <div class="grid grid-cols-12 items-center py-2 px-2 rounded-lg table-row-hover transition-colors">
        <span class="col-span-1 ${rankColor} text-[11px]">${r.rank}</span>
        <div class="col-span-6 flex items-center space-x-2 truncate">
          <img src="${r.logo}" onerror="this.style.display='none'" class="w-4 h-4 object-contain">
          <span class="truncate font-medium text-gray-200 text-xs">${r.team_name}</span>
        </div>
        <span class="col-span-1 text-center text-gray-400 text-xs">${r.played}</span>
        <span class="col-span-1 text-center text-gray-400 text-xs">${r.wins}</span>
        <span class="col-span-1 text-center text-gray-400 text-xs">${r.draws}</span>
        <span class="col-span-1 text-center text-gray-400 text-xs">${r.losses}</span>
        <span class="col-span-1 text-right font-bold text-gray-100 text-xs">${r.points}</span>
      </div>
    `;
  }).join('');
}

// Match Detail Modal Logic
async function openMatchModal(leagueId, eventId) {
  const match = state.matches.find(m => m.id === eventId);
  if (!match) return;

  state.activeModalMatch = match;

  // Set modal elements
  document.getElementById('modalLeagueName').textContent = match.league_name;
  document.getElementById('modalVenue').textContent = match.venue || 'Stadium';
  document.getElementById('modalHomeLogo').src = match.home.logo;
  document.getElementById('modalHomeName').textContent = match.home.name;
  document.getElementById('modalAwayLogo').src = match.away.logo;
  document.getElementById('modalAwayName').textContent = match.away.name;
  document.getElementById('modalScoreHome').textContent = match.home.score;
  document.getElementById('modalScoreAway').textContent = match.away.score;
  document.getElementById('modalClockText').textContent = match.clock || (match.is_finished ? 'Full Time' : 'Upcoming');
  document.getElementById('modalBroadcastText').textContent = match.broadcast || 'Live Feed';
  document.getElementById('modalHeadline').textContent = match.headline || '';

  const modal = document.getElementById('matchDetailModal');
  modal.classList.remove('hidden');

  // Load summary details
  setModalTab('events');
  try {
    const res = await fetch(`/api/match/${leagueId}/${eventId}`);
    const result = await res.json();
    if (result.success && result.data) {
      renderModalDetails(result.data);
    }
  } catch (err) {
    console.error('Error fetching match details:', err);
  }
}

function setModalTab(tab) {
  state.activeModalTab = tab;
  const eventsBtn = document.getElementById('modalTabEventsBtn');
  const statsBtn = document.getElementById('modalTabStatsBtn');
  const eventsCont = document.getElementById('modalEventsContainer');
  const statsCont = document.getElementById('modalStatsContainer');

  if (tab === 'events') {
    eventsBtn.className = 'flex-1 py-3 text-center border-b-2 border-blue-500 text-blue-400 transition-colors font-bold';
    statsBtn.className = 'flex-1 py-3 text-center border-b-2 border-transparent text-gray-400 hover:text-white transition-colors font-bold';
    eventsCont.classList.remove('hidden');
    statsCont.classList.add('hidden');
  } else {
    statsBtn.className = 'flex-1 py-3 text-center border-b-2 border-blue-500 text-blue-400 transition-colors font-bold';
    eventsBtn.className = 'flex-1 py-3 text-center border-b-2 border-transparent text-gray-400 hover:text-white transition-colors font-bold';
    statsCont.classList.remove('hidden');
    eventsCont.classList.add('hidden');
  }
}

function renderModalDetails(data) {
  // 1. Events Timeline
  const eventsCont = document.getElementById('modalEventsContainer');
  const events = data.events || [];
  if (events.length === 0) {
    eventsCont.innerHTML = `<p class="text-xs text-gray-500 text-center py-6">No major events recorded yet.</p>`;
  } else {
    eventsCont.innerHTML = events.map(ev => {
      let icon = '⚽';
      let badgeClass = 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';

      if (ev.type === 'yellow') {
        icon = '🟨';
        badgeClass = 'bg-amber-500/10 text-amber-400 border border-amber-500/20';
      } else if (ev.type === 'red') {
        icon = '🟥';
        badgeClass = 'bg-red-500/10 text-red-400 border border-red-500/20';
      } else if (ev.type === 'basket') {
        icon = '🏀';
      }

      return `
        <div class="flex items-start space-x-3 p-3 rounded-xl bg-gray-900/60 border border-gray-800 text-xs">
          <span class="px-2 py-0.5 rounded font-mono font-bold ${badgeClass}">
            ${ev.clock || 'Event'}
          </span>
          <div class="flex-1">
            <span class="mr-1">${icon}</span>
            <span class="text-gray-200">${ev.text}</span>
          </div>
        </div>
      `;
    }).join('');
  }

  // 2. Stats Bars
  const statsCont = document.getElementById('modalStatsContainer');
  const stats = data.stats || [];
  if (stats.length === 0) {
    statsCont.innerHTML = `<p class="text-xs text-gray-500 text-center py-6">In-depth statistics not available for this event.</p>`;
  } else {
    statsCont.innerHTML = stats.map(s => {
      const hNum = parseFloat(s.home) || 0;
      const aNum = parseFloat(s.away) || 0;
      const total = hNum + aNum;
      const homePct = total > 0 ? Math.round((hNum / total) * 100) : 50;
      const awayPct = 100 - homePct;

      return `
        <div class="space-y-1">
          <div class="flex items-center justify-between text-xs font-semibold text-gray-300">
            <span>${s.home}</span>
            <span class="text-gray-400 uppercase tracking-wider text-[11px]">${s.label}</span>
            <span>${s.away}</span>
          </div>
          <div class="h-2 w-full bg-gray-800 rounded-full overflow-hidden flex">
            <div class="h-full bg-blue-500 transition-all duration-500" style="width: ${homePct}%"></div>
            <div class="h-full bg-emerald-500 transition-all duration-500" style="width: ${awayPct}%"></div>
          </div>
        </div>
      `;
    }).join('');
  }
}

function closeModal() {
  const modal = document.getElementById('matchDetailModal');
  if (modal) modal.classList.add('hidden');
}

// Close modal when clicking outside
window.addEventListener('click', (e) => {
  const modal = document.getElementById('matchDetailModal');
  if (e.target === modal) {
    closeModal();
  }
});
