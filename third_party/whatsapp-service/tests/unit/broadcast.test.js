const assert = require('assert');
const {
    getBroadcastProgress,
    stopBroadcast,
    calculateInterval,
} = require('../../src/services/broadcast');

describe('Broadcast Service', function () {
    describe('getBroadcastProgress()', function () {
        it('should return broadcast progress object', function () {
            const progress = getBroadcastProgress();
            assert.strictEqual(typeof progress.running, 'boolean');
            assert.strictEqual(typeof progress.current, 'number');
            assert.strictEqual(typeof progress.total, 'number');
        });
    });

    describe('stopBroadcast()', function () {
        it('should set running to false', function () {
            stopBroadcast();
            const progress = getBroadcastProgress();
            assert.strictEqual(progress.running, false);
        });
    });

    describe('calculateInterval()', function () {
        it('should return interval greater than minInterval', function () {
            const limit = { minInterval: 60000 };
            const result = calculateInterval(10000, false, limit);
            assert.ok(result.interval >= 60000);
        });

        it('should return random interval when randomInterval is true', function () {
            const limit = { minInterval: 60000 };
            const result1 = calculateInterval(10000, true, limit);
            const result2 = calculateInterval(10000, true, limit);
            assert.ok(result1.interval >= 60000);
            assert.ok(result2.interval >= 60000);
        });
    });
});
