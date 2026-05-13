const assert = require('assert');
const {
    canSend,
    recordSend,
    getDailyStats,
    setAccountLevel,
    getCurrentLimit,
} = require('../../src/services/rate-limiter');

describe('Rate Limiter', function () {
    beforeEach(function () {
        setAccountLevel('new');
    });

    describe('canSend()', function () {
        it('should allow sending when under daily limit', function () {
            const result = canSend();
            assert.strictEqual(result.allowed, true);
            assert.strictEqual(result.dailyMax, 30);
        });

        it('should block sending when daily limit reached', function () {
            for (let i = 0; i < 30; i++) {
                recordSend(true);
            }
            const result = canSend();
            assert.strictEqual(result.allowed, false);
            assert.strictEqual(result.reason, 'daily_limit');
        });
    });

    describe('setAccountLevel()', function () {
        it('should set new account level correctly', function () {
            setAccountLevel('new');
            const limit = getCurrentLimit();
            assert.strictEqual(limit.dailyMax, 30);
        });

        it('should set established account level correctly', function () {
            setAccountLevel('established');
            const limit = getCurrentLimit();
            assert.strictEqual(limit.dailyMax, 80);
        });

        it('should set mature account level correctly', function () {
            setAccountLevel('mature');
            const limit = getCurrentLimit();
            assert.strictEqual(limit.dailyMax, 150);
        });
    });

    describe('getDailyStats()', function () {
        it('should return current daily stats', function () {
            const stats = getDailyStats();
            assert.strictEqual(typeof stats.sent, 'number');
            assert.strictEqual(typeof stats.dailyMax, 'number');
        });
    });
});
