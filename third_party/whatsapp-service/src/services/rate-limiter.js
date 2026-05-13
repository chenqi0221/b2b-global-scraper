const { SAFE_LIMITS } = require('../../config/rate-limits');

let dailySendStats = {
    date: new Date().toDateString(),
    sent: 0,
    failed: 0,
    paused: 0,
};

let currentLimitLevel = SAFE_LIMITS.NEW_ACCOUNT;

function resetDailyStatsIfNewDay() {
    const today = new Date().toDateString();
    if (dailySendStats.date !== today) {
        dailySendStats = {
            date: today,
            sent: 0,
            failed: 0,
            paused: 0,
        };
    }
}

function canSend() {
    resetDailyStatsIfNewDay();
    const limit = currentLimitLevel;

    if (dailySendStats.sent >= limit.dailyMax) {
        return { allowed: false, reason: 'daily_limit', remaining: 0 };
    }

    const remaining = limit.dailyMax - dailySendStats.sent;
    return {
        allowed: true,
        remaining,
        dailyMax: limit.dailyMax,
        sent: dailySendStats.sent,
    };
}

function recordSend(success = true) {
    resetDailyStatsIfNewDay();
    if (success) {
        dailySendStats.sent++;
    } else {
        dailySendStats.failed++;
    }
}

function getDailyStats() {
    resetDailyStatsIfNewDay();
    return { ...dailySendStats, dailyMax: currentLimitLevel.dailyMax };
}

function setAccountLevel(level) {
    if (level === 'new') {
        currentLimitLevel = SAFE_LIMITS.NEW_ACCOUNT;
    } else if (level === 'established') {
        currentLimitLevel = SAFE_LIMITS.ESTABLISHED_ACCOUNT;
    } else if (level === 'mature') {
        currentLimitLevel = SAFE_LIMITS.MATURE_ACCOUNT;
    }
}

function getCurrentLimit() {
    return currentLimitLevel;
}

module.exports = {
    canSend,
    recordSend,
    getDailyStats,
    setAccountLevel,
    getCurrentLimit,
};
