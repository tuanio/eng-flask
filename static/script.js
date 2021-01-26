var listVoices = [];
let synth = window.speechSynthesis;

function play(e, link) {
    e.preventDefault();
    let txt = link.getAttribute('data-english');
    let synth = window.speechSynthesis;
    let toSpeak = new SpeechSynthesisUtterance(txt);
    let userVoiceIndex = link.dataset.voiceIndex;
    for (i of listVoices) {
        if (i[1] == userVoiceIndex) {
            toSpeak.voice = i[0];
        }
    }
    synth.speak(toSpeak);
}

function getVoices(voices) {
    let idx = 0;
    for (i of voices) {
        if (i['lang'].slice(0, 2) == 'en') {
            listVoices.push([i, idx++]);
        }
    }
}   

function loading() {
    let option = document.querySelector("#voice-select");
    if (listVoices == 0) getVoices(synth.getVoices());

    let userVoiceIndex = document.querySelector('#voice-user-index').textContent;

    let data = '';
    for (let i = 0; i < listVoices.length; i++) {
        if (listVoices[i][1] == userVoiceIndex) {
            data = listVoices[i];
            listVoices.splice(i, 1);
            break;
        }
    }
    listVoices.unshift(data);

    listVoices.forEach((voice) => {
        let listItem = document.createElement('option');
        listItem.textContent = voice[0].name;
        listItem.setAttribute('value', voice[1]);
        listItem.setAttribute('data-lang', voice[0].lang);
        listItem.setAttribute('data-name', voice[0].name);
        option.appendChild(listItem);
    });
}


function voiceFunc(option) {
    let speaker = new SpeechSynthesisUtterance("Hello World");
    let selectedIndex = option.value;
    for (i of listVoices) {
        if (i[1] == selectedIndex) {
            speaker.voice = i[0];
        }
    }
    synth.speak(speaker);
}