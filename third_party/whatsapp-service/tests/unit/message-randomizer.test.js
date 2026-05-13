const assert = require('assert');
const { randomizeMessage } = require('../../src/services/message-randomizer');

describe('Message Randomizer', function () {
    describe('randomizeMessage()', function () {
        it('should return an object with message and greeting', function () {
            const result = randomizeMessage('Hello world');
            assert.strictEqual(typeof result.message, 'string');
            assert.ok(
                result.greeting === null || typeof result.greeting === 'string',
            );
        });

        it('should detect greeting at the start', function () {
            const result = randomizeMessage('Hi there, how are you?');
            assert.strictEqual(result.greeting, 'Hi');
        });

        it('should change greeting if same as lastGreeting', function () {
            const result = randomizeMessage('Hello world', 'Hello');
            assert.notStrictEqual(result.greeting, 'Hello');
        });

        it('should preserve message content when lengthRandomize is false', function () {
            const original = 'Hello world';
            const result = randomizeMessage(original, null, false);
            assert.strictEqual(result.message, original);
        });

        it('should process message when lengthRandomize is true', function () {
            const original =
                'This is a test message that should be long enough for length randomization.';
            const result = randomizeMessage(original, null, true);
            assert.strictEqual(typeof result.message, 'string');
            assert.ok(result.message.length > 0);
        });

        it('should handle messages without greetings', function () {
            const result = randomizeMessage(
                'Just a regular message without greeting',
            );
            assert.strictEqual(result.greeting, null);
        });
    });
});
