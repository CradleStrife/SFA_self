document.addEventListener("DOMContentLoaded", function() {
    const serotypes = JSON.parse(document.getElementById('serotype-data').textContent);
    console.log(serotypes);

    const wordCount = serotypes.reduce((acc, word) => {
        acc[word] = acc[word] ? acc[word] + 1 : 1;
        return acc;
    }, {});

    console.log(wordCount);
    const wordArray = Object.keys(wordCount).map(word => [word, wordCount[word]]);
    console.log(wordArray);

    if (typeof WordCloud === 'undefined') {
        console.error("WordCloud function is not defined. Ensure the wordcloud2.js script is loaded.");
        return;
    }

    function getRandomColor() {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    const tooltip = document.createElement('div');
    tooltip.style.position = 'absolute';
    tooltip.style.backgroundColor = '#333';
    tooltip.style.color = '#fff';
    tooltip.style.padding = '5px';
    tooltip.style.borderRadius = '5px';
    tooltip.style.display = 'none';
    tooltip.style.pointerEvents = 'none'; // Ensure the tooltip does not interfere with mouse events
    document.body.appendChild(tooltip);

    WordCloud(document.getElementById('word-cloud'), {
        list: wordArray,
        gridSize: Math.round(16 * document.getElementById('word-cloud').offsetWidth / 1024),
        weightFactor: 20,
        fontFamily: 'Times, serif',
        color: getRandomColor,
        rotateRatio: 0.5,
        rotationSteps: 2,
        backgroundColor: '#ffffff',
        drawOutOfBound: false,
        hover: function(item, dimension, event) {
            if (item) {
                tooltip.innerHTML = `${item[0]}: ${item[1]}`;
                tooltip.style.left = `${event.pageX}px`;
                tooltip.style.top = `${event.pageY - 40}px`; // Adjust position to appear above the cursor
                tooltip.style.display = 'block';
            } else {
                tooltip.style.display = 'none'; // Hide tooltip when hovering out
            }
        }
    });
});
