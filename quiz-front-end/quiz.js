class SPARQLQueryDispatcher {
	constructor( endpoint ) {
		this.endpoint = endpoint;
	}

	query( sparqlQuery ) {
		const fullUrl = this.endpoint + '?query=' + encodeURIComponent( sparqlQuery );
		const headers = { 'Accept': 'application/sparql-results+json', 'Access-Control-Allow-Origin': '*' };

		return fetch( fullUrl, { headers } ).then( body => body.json() );
	}
}

const endpointUrl = 'http://localhost:7200/repositories/ferhengo';
const queryDispatcher = new SPARQLQueryDispatcher( endpointUrl );
var leker_s = new Set();
var leker_l = [];
var word_l = [];
var quiz_d = {};

const lekerQuery = `PREFIX lexinfo: <http://www.lexinfo.net/ontology/2.0/lexinfo#>
SELECT DISTINCT ?item ?item2
WHERE {
    ?item lexinfo:synonym ?item2 .
}`;

async function get_far_related_l(word) {
    var sparqlQuery = `PREFIX lexinfo: <http://www.lexinfo.net/ontology/2.0/lexinfo#>
    PREFIX base: <http://ferhengo-ontolex-graph.com/>
    SELECT DISTINCT ?item
    WHERE {
        { base:${word}_v_ku_sense lexinfo:synonym ?item . }
        UNION
        { ?item lexinfo:synonym base:${word}_v_ku_sense . }
        UNION
        {
            ?item lexinfo:synonym ?item2 .
            ?item2 lexinfo:synonym base:${word}_v_ku_sense .
        }
        UNION
        {
            ?item lexinfo:synonym ?item2 .
            ?item2 lexinfo:synonym ?item3 .
            ?item3 lexinfo:synonym base:${word}_v_ku_sense .
        }
        UNION
        {
            ?item lexinfo:synonym ?item2 .
            ?item2 lexinfo:synonym ?item3 .
            ?item3 lexinfo:synonym ?item4 .
            ?item4 lexinfo:synonym base:${word}_v_ku_sense .
        }
    }`;

    var result = [];
    await queryDispatcher.query( sparqlQuery ).then(
        body => {
            body.results.bindings.forEach( function ( item ) {
                result.push(item.item.value.replace('http://ferhengo-ontolex-graph.com/', '').replace('_v_ku_sense', '').replaceAll('-', ' '));
            } );
        }
    );
    return result;
}

async function get_related_l(word) {
    var sparqlQuery = `PREFIX lexinfo: <http://www.lexinfo.net/ontology/2.0/lexinfo#>
    PREFIX base: <http://ferhengo-ontolex-graph.com/>
    SELECT DISTINCT ?item
    WHERE {
        { base:${word}_v_ku_sense lexinfo:synonym ?item . }
        UNION
        { ?item lexinfo:synonym base:${word}_v_ku_sense . }
        UNION
        {
            ?item lexinfo:synonym ?item2 .
            ?item2 lexinfo:synonym base:${word}_v_ku_sense .
        }
        FILTER (?item != base:${word}_v_ku_sense)
    }`;

    var result = [];
    await queryDispatcher.query( sparqlQuery ).then(
        body => {
            body.results.bindings.forEach( function ( item ) {
                result.push(item.item.value.replace('http://ferhengo-ontolex-graph.com/', '').replace('_v_ku_sense', '').replaceAll('-', ' '));
            } );
        }
    );
    return result;
}

var quiz_len = 3;
const word_id_l = ['word1', 'word2', 'word3'];
var word_index = 0;
var random_index;
var result_d = {};
var correct_count = 0;

function create_quiz() {
    var p = document.createElement('p');
    p.id = 'header';
    p.classList.add('h1', 'text-center');
    p.innerHTML = 'Find the related word';
    document.getElementById('quiz').appendChild(p);
    p = document.createElement('p');
    p.id = 'gold';
    p.classList.add('h2', 'text-center');
    p.style.color = 'orange';
    document.getElementById('quiz').appendChild(p);
    var buttons = document.createElement('div');
    buttons.id = 'buttons';
    document.getElementById('quiz').appendChild(buttons);
    word_id_l.forEach(word_id => {
        var button = document.createElement('button');
        button.id = word_id;
        button.type = 'button';
        button.classList.add('btn', 'btn-light', 'btn-lg', 'btn-block', 'm-1');
        button.addEventListener('click', function() { check_word(this.id); });
        document.getElementById('buttons').appendChild(button);
    });
    p = document.createElement('p');
    p.id = 'result';
    document.getElementById('quiz').appendChild(p);
}

function refresh_buttons() {
    word_id_l.forEach(word_id => { 
        let word = document.getElementById(word_id);
        if (word.classList.contains('btn-success')) {
            word.classList.remove('btn-success');
            word.classList.add('btn-light');
        } else if (word.classList.contains('btn-danger')) {
            word.classList.remove('btn-danger');
            word.classList.add('btn-light');
        } else if (word.classList.contains('btn-secondary')) {
            word.classList.remove('btn-secondary');
            word.classList.add('btn-light');
        }
    });
}

function update_quiz() {
    refresh_buttons();
    document.getElementById('result').innerHTML = '';
    if (word_index < quiz_len) {
        document.getElementById('result').innerHTML = 'Correct: ' + correct_count + '/' + word_index;
    }
    var word = word_l[word_index];
    document.getElementById('gold').innerHTML = word + '<br>';
    var related_word = quiz_d[word][0];
    var unrelated_word_l = quiz_d[word].slice(1);
    var indices_l = [0, 1, 2];
    random_index = Math.floor(Math.random() * 3);
    document.getElementById(word_id_l[random_index]).innerHTML = related_word;
    indices_l.splice(random_index, 1);
    document.getElementById(word_id_l[indices_l[0]]).innerHTML = unrelated_word_l[0];
    document.getElementById(word_id_l[indices_l[1]]).innerHTML = unrelated_word_l[1];
    word_index++;
};

function clear_quiz() {
    let gold = document.getElementById('gold');
    if (gold) {
        gold.remove();
    }
    let buttons = document.getElementById('buttons');
    if (buttons) {
        buttons.remove();
    }
}

function finish_quiz() {
    clear_quiz();
    document.getElementById('result').innerHTML = `Quiz finished! You have ${correct_count} correct answers, out of ${quiz_len} questions.`;
    var table = document.createElement('table');
    table.id = 'result_table';
    table.classList.add('table', 'table-striped', 'table-bordered', 'table-hover', 'table-sm');
    var thead = document.createElement('thead');
    var tr = document.createElement('tr');
    var th = document.createElement('th');
    th.scope = 'col';
    th.innerHTML = 'Index';
    tr.appendChild(th);
    th = document.createElement('th');
    th.scope = 'col';
    th.innerHTML = 'Word';
    tr.appendChild(th);
    th = document.createElement('th');
    th.scope = 'col';
    th.innerHTML = 'Correct choice';
    tr.appendChild(th);
    th = document.createElement('th');
    th.scope = 'col';
    th.innerHTML = 'Your choice';
    tr.appendChild(th);
    thead.appendChild(tr);
    table.appendChild(thead);
    var tbody = document.createElement('tbody');
    var index = 1;
    Object.keys(result_d).forEach(word => {
        tr = document.createElement('tr');
        var td = document.createElement('td');
        td.innerHTML = index++;
        tr.appendChild(td);
        td = document.createElement('td');
        td.innerHTML = word;
        tr.appendChild(td);
        td = document.createElement('td');
        td.innerHTML = result_d[word][0];
        tr.appendChild(td);
        td = document.createElement('td');
        td.innerHTML = result_d[word][1];
        tr.appendChild(td);
        if (result_d[word][0] == result_d[word][1]) {
            tr.classList.add('table-success');
        } else {
            tr.classList.add('table-danger');
        }
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    document.getElementById('quiz').appendChild(table);
    var button = document.createElement('button');
    button.id = 'replay';
    button.type = 'button';
    button.classList.add('btn', 'btn-light', 'btn-lg', 'btn-block', 'm-1');
    button.setAttribute('onclick', 'refresh_page()');
    button.innerHTML = 'Replay?';
    document.getElementById('quiz').appendChild(button);
};

function refresh_page() {
    location.reload();
}

function check_word(word) {
    if (word_id_l[random_index] == word) {
        document.getElementById(word).classList.remove('btn-light');
        document.getElementById(word).classList.add('btn-success');
        document.getElementById('result').innerHTML = 'Correct!';
        correct_count++;
    } else {
        document.getElementById(word).classList.remove('btn-light');
        document.getElementById(word).classList.add('btn-danger');
        document.getElementById(word_id_l[random_index]).classList.remove('btn-light');
        document.getElementById(word_id_l[random_index]).classList.add('btn-secondary');
        document.getElementById('result').innerHTML = 'Incorrect!';
    }
    result_d[word_l[word_index - 1]] = [quiz_d[word_l[word_index - 1]][0], document.getElementById(word).innerHTML];
    if (word_index < word_l.length) {
        setTimeout(update_quiz, 1000);
    } else {
        setTimeout(finish_quiz, 1000);
    }
};

queryDispatcher.query( lekerQuery ).then(
    body => {
        body.results.bindings.forEach( function ( item ) {
            leker_s.add( item.item.value.replace('http://ferhengo-ontolex-graph.com/', '').replace('_v_ku_sense', '').replaceAll('-', ' ') );
            leker_s.add( item.item2.value.replace('http://ferhengo-ontolex-graph.com/', '').replace('_v_ku_sense', '').replaceAll('-', ' ') );
        } );
        leker_l = Array.from(leker_s);
    }
).then(
    async function () {
        while (word_l.length < quiz_len) {
            var random_word = leker_l[Math.floor(Math.random() * leker_l.length)];
            if (word_l.includes(random_word)) {
                continue;
            }
            var word = random_word.replaceAll(' ', '-');
            var related_l = await get_related_l(word);
            var filtered_l = [];
            related_l.forEach(related_word => {
                if (similarity(word, related_word) < 0.7) {
                    filtered_l.push(related_word);
                }
            });
            if (filtered_l.length == 0) {
                continue;
            }
            var related_word = filtered_l[Math.floor(Math.random() * filtered_l.length)];
            var far_related_l = await get_far_related_l(word);
            var unrelated_word_l = [];
            while (unrelated_word_l.length < 2) {
                var random_word = leker_l[Math.floor(Math.random() * leker_l.length)];
                if (!unrelated_word_l.includes(random_word) && !far_related_l.includes(random_word)) {
                    unrelated_word_l.push(random_word);
                }
            }
            word_l.push(word.replaceAll('-', ' '));
            quiz_d[word.replaceAll('-', ' ')] = [related_word, unrelated_word_l[0], unrelated_word_l[1]];
        }
    }
).then(
    function () {
        create_quiz();
        update_quiz();
    }
);

function checkSimilarity(){
    var str1 = document.getElementById("lhsInput").value;
    var str2 = document.getElementById("rhsInput").value;
    document.getElementById("output").innerHTML = similarity(str1, str2);
}

function similarity(s1, s2) {
    var longer = s1;
    var shorter = s2;
    if (s1.length < s2.length) {
        longer = s2;
        shorter = s1;
    }
    var longerLength = longer.length;
    if (longerLength == 0) {
        return 1.0;
    }
    return (longerLength - editDistance(longer, shorter)) / parseFloat(longerLength);
}

function editDistance(s1, s2) {
    s1 = s1.toLowerCase();
    s2 = s2.toLowerCase();

    var costs = new Array();
    for (var i = 0; i <= s1.length; i++) {
        var lastValue = i;
        for (var j = 0; j <= s2.length; j++) {
            if (i == 0)
                costs[j] = j;
            else {
                if (j > 0) {
                    var newValue = costs[j - 1];
                    if (s1.charAt(i - 1) != s2.charAt(j - 1)) {
                        newValue = Math.min(Math.min(newValue, lastValue), costs[j]) + 1;
                    }
                    costs[j - 1] = lastValue;
                    lastValue = newValue;
                }
            }
        }
        if (i > 0) {
            costs[s2.length] = lastValue;
        }
    }
    return costs[s2.length];
}