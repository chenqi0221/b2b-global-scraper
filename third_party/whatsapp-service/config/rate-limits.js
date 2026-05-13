const SAFE_LIMITS = {
    NEW_ACCOUNT: {
        dailyMax: 30,
        hourlyMax: 5,
        minInterval: 60000,
        batchSize: 5,
        batchPause: 180000,
    },
    ESTABLISHED_ACCOUNT: {
        dailyMax: 80,
        hourlyMax: 10,
        minInterval: 30000,
        batchSize: 10,
        batchPause: 120000,
    },
    MATURE_ACCOUNT: {
        dailyMax: 150,
        hourlyMax: 20,
        minInterval: 20000,
        batchSize: 15,
        batchPause: 60000,
    },
};

module.exports = { SAFE_LIMITS };
