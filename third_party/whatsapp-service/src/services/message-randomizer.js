function randomizeMessage(
    message,
    lastGreeting = null,
    lengthRandomize = true,
) {
    let result = message;

    const greetings = [
        'Hi',
        'Hey',
        'Hello',
        'Greetings',
        'Hi there',
        'Hey there',
        'Good morning',
        'Good afternoon',
        'Good evening',
    ];
    let currentGreeting = null;

    for (const greeting of greetings) {
        const cleanStart = result
            .replace(
                /^[\s\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]+/u,
                '',
            )
            .trim();
        if (cleanStart.toLowerCase().startsWith(greeting.toLowerCase())) {
            currentGreeting = greeting;
            break;
        }
    }

    if (currentGreeting && currentGreeting === lastGreeting) {
        const otherGreetings = greetings.filter((g) => g !== currentGreeting);
        const newGreeting =
            otherGreetings[Math.floor(Math.random() * otherGreetings.length)];
        const regex = new RegExp(
            `^([\\s\\u{1F300}-\\u{1F9FF}\\u{2600}-\\u{26FF}\\u{2700}-\\u{27BF}]*)${currentGreeting}`,
            'iu',
        );
        result = result.replace(regex, `$1${newGreeting}`);
        currentGreeting = newGreeting;
    }

    const emojis = [
        '😊',
        '👍',
        '✨',
        '🎉',
        '👋',
        '😄',
        '🙏',
        '🌟',
        '💐',
        '🤝',
        '🌈',
        '🎊',
        '💖',
        '🌺',
        '💫',
        '🦋',
        '🏆',
        '💎',
        '🔥',
        '⭐',
    ];

    if (Math.random() < 0.2) {
        const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
        if (Math.random() < 0.5) {
            result = randomEmoji + ' ' + result;
        } else {
            result = result + ' ' + randomEmoji;
        }
    }

    if (Math.random() < 0.25) {
        const synonyms = {
            project: ['venture', 'endeavor', 'initiative', 'undertaking'],
            collection: ['range', 'lineup', 'selection', 'series'],
            new: ['latest', 'fresh', 'brand-new', 'innovative'],
            quality: ['premium', 'top-tier', 'high-end', 'superior'],
            contact: ['reach out', 'get in touch', 'connect'],
            offer: ['proposal', 'opportunity', 'deal', 'package'],
            exclusive: ['limited', 'special', 'VIP', 'premium'],
            amazing: ['incredible', 'outstanding', 'remarkable', 'fantastic'],
            interested: ['keen', 'intrigued', 'enthusiastic'],
            reply: ['respond', 'write back', 'message back'],
        };

        for (const [word, alternatives] of Object.entries(synonyms)) {
            const regex = new RegExp(`\\b${word}\\b`, 'gi');
            if (regex.test(result) && Math.random() < 0.3) {
                const replacement =
                    alternatives[
                        Math.floor(Math.random() * alternatives.length)
                    ];
                result = result.replace(regex, (match) => {
                    if (match[0] === match[0].toUpperCase()) {
                        return (
                            replacement.charAt(0).toUpperCase() +
                            replacement.slice(1)
                        );
                    }
                    return replacement;
                });
            }
        }
    }

    if (Math.random() < 0.2) {
        const transformations = [
            { from: /\bWe are excited to\b/gi, to: "We're thrilled to" },
            { from: /\bDon't hesitate to\b/gi, to: 'Feel free to' },
            { from: /\bLooking forward to\b/gi, to: "Can't wait to" },
            {
                from: /\bThank you for your interest\b/gi,
                to: 'Thanks for your interest',
            },
            { from: /\bPlease let us know\b/gi, to: 'Let us know' },
            { from: /\bWe would love to\b/gi, to: "We'd love to" },
        ];

        const randomTransform =
            transformations[Math.floor(Math.random() * transformations.length)];
        if (randomTransform.from.test(result)) {
            result = result.replace(randomTransform.from, randomTransform.to);
        }
    }

    if (Math.random() < 0.15) {
        const closings = [
            'Looking forward to hearing from you!',
            'Excited to connect with you!',
            'Have a wonderful day!',
            'Best regards',
            'Talk soon!',
            'Cheers',
            'Stay amazing!',
            "Can't wait to work together!",
        ];
        const randomClosing =
            closings[Math.floor(Math.random() * closings.length)];
        result = result + '\n\n' + randomClosing;
    }

    if (Math.random() < 0.2) {
        const sentences = result.split('.');
        if (sentences.length > 2) {
            for (let i = 0; i < sentences.length - 1; i++) {
                if (Math.random() < 0.3) {
                    sentences[i] = sentences[i].trim() + '!';
                } else {
                    sentences[i] = sentences[i].trim() + '.';
                }
            }
            result = sentences.join(' ');
        }
    }

    if (lengthRandomize) {
        const optionalPhrases = [
            { add: ' By the way, ', prob: 0.15 },
            { add: ' Just a quick note: ', prob: 0.1 },
            { add: ' Also, ', prob: 0.12 },
            { add: ' Plus, ', prob: 0.1 },
            { add: ' In addition, ', prob: 0.08 },
            { add: ' As a side note, ', prob: 0.06 },
            { add: ' FYI, ', prob: 0.1 },
            { add: ' Just so you know, ', prob: 0.08 },
        ];

        const sentencesArr = result.split(/(?<=[.!?])\s+/);
        if (sentencesArr.length > 1) {
            for (const phrase of optionalPhrases) {
                if (Math.random() < phrase.prob) {
                    const insertIdx =
                        Math.floor(Math.random() * (sentencesArr.length - 1)) +
                        1;
                    sentencesArr[insertIdx] =
                        phrase.add +
                        sentencesArr[insertIdx].toLowerCase().charAt(0) +
                        sentencesArr[insertIdx].slice(1);
                    break;
                }
            }
            result = sentencesArr.join(' ');
        }

        const fillerWords = [
            { pattern: /\bvery\b/gi, replacement: 'really', prob: 0.1 },
            { pattern: /\breally\b/gi, replacement: 'very', prob: 0.1 },
            { pattern: /\bgreat\b/gi, replacement: 'wonderful', prob: 0.1 },
            { pattern: /\bwonderful\b/gi, replacement: 'great', prob: 0.1 },
        ];

        for (const fw of fillerWords) {
            if (Math.random() < fw.prob && fw.pattern.test(result)) {
                result = result.replace(fw.pattern, fw.replacement);
            }
        }

        if (Math.random() < 0.2 && currentGreeting) {
            const namePlaceholders = ['{name}', 'there', 'friend', 'pal'];
            const placeholder =
                namePlaceholders[
                    Math.floor(Math.random() * namePlaceholders.length)
                ];
            const greetingRegex = new RegExp(
                `^([\\s\\u{1F300}-\\u{1F9FF}\\u{2600}-\\u{26FF}\\u{2700}-\\u{27BF}]*${currentGreeting})([,!\\s]*)`,
                'iu',
            );
            if (!result.match(new RegExp(`${currentGreeting}\\s+\\w+`, 'i'))) {
                result = result.replace(greetingRegex, `$1 ${placeholder}$2`);
            }
        }

        if (Math.random() < 0.4) {
            const invisibleChars = ['\u200B', '\u200C', '\u200D', '\uFEFF'];
            const chars = result.split('');
            const insertPositions = [];
            const insertCount = Math.floor(Math.random() * 4) + 2;
            for (let i = 0; i < insertCount; i++) {
                const pos = Math.floor(Math.random() * chars.length);
                insertPositions.push(pos);
            }
            insertPositions.sort((a, b) => b - a);
            for (const pos of insertPositions) {
                const randomChar =
                    invisibleChars[
                        Math.floor(Math.random() * invisibleChars.length)
                    ];
                chars.splice(pos, 0, randomChar);
            }
            result = chars.join('');
        }

        if (Math.random() < 0.3) {
            const extraSpaces = Math.floor(Math.random() * 2) + 1;
            result = result.replace(/([.!?])(\s)/g, (match, p1) => {
                if (Math.random() < 0.4) {
                    return p1 + ' '.repeat(extraSpaces);
                }
                return match;
            });
        }

        if (Math.random() < 0.15 && result.length > 100) {
            const words = result.split(' ');
            if (words.length > 10) {
                const breakPos =
                    Math.floor(Math.random() * (words.length - 5)) + 3;
                words.splice(breakPos, 0, '\n');
                result = words.join(' ');
            }
        }

        if (Math.random() < 0.1) {
            const punctuationVariations = [
                { from: /,\s+/g, to: '... ', prob: 0.05 },
                { from: /;\s+/g, to: ' — ', prob: 0.05 },
            ];
            for (const pv of punctuationVariations) {
                if (Math.random() < pv.prob) {
                    result = result.replace(pv.from, pv.to);
                }
            }
        }
    }

    return {
        message: result,
        greeting: currentGreeting,
    };
}

module.exports = { randomizeMessage };
