const fs = require('fs');
const spawn = require('child_process').spawn;
const util = require('util');
const readFile = util.promisify(fs.readFile);
const moment = require('moment-timezone');
const OBSWebSocket = require('obs-websocket-js');
const obs = new OBSWebSocket();
let random = require('random-js')();
const serve = require('serve');

const HOST = 'localhost:4444';
const PASS = 'autotv';
const BASE = '/home/sam/autotv';

const SOURCES = ["video", "image", "text1", "window", "audio1", "audio2", "browser", "vlc"];

let procs = [];
let server;
let timeout;
let currentShow = null;
let showCodes = {
  'Cop Show': copShow,
  'Shopping Show': laborShow,
  'Meditation Show': meditationShow,
  'Cooking Show': cookingShow,
  'Advice Show': tipsShow,
  'Home Show': homeInvaderShow,
  'Nature Show': natureShow
};


async function cleanup() {
  clearTimeout(timeout);
  procs.forEach((p) => {
    p.kill()
  });
  spawn('killall', ['-9', 'meditationshow']);
}

async function createWebServer(path, port=8000) {
  if (server) server.stop();
  server = serve(path, {port: port});
  return `http://localhost:${port}`;
}

async function switchScene(name, transition = 'Fade', duration = 1000) {
  await obs.SetCurrentScene({'scene-name': name});
  return true;
}

async function updateMedia(id, filename) {
  return await obs.SetSourceSettings({
    sourceName: id,
    sourceSettings: {
      local_file: filename
    }
  });
}

async function setVideo(filename){
  await obs.SetSourceSettings({
    sourceName: 'video',
    sourceSettings: {
      local_file: filename
    }
  });
  return await show('video');
}

async function setAudio(filename){
  let settings = await obs.SetSourceSettings({
    sourceName: 'audio1',
    sourceSettings: {
      local_file: filename
    }
  });
  return await show('audio1');
}

async function setAudio2(filename){
  await obs.SetSourceSettings({
    sourceName: 'audio2',
    sourceSettings: {
      local_file: filename
    }
  });
  return await show('audio2');
}

async function updateURL(id, value) {
  return await obs.SetSourceSettings({
    sourceName: id,
    sourceSettings: {
      url: value
    }
  });
}

async function setLocalURL(value) {
  await obs.SetSourceSettings({
    sourceName: 'browser',
    sourceSettings: {
      local_file: value
    }
  });
  return await show('browser');
}

async function setRemoteURL(value) {
  await obs.SetSourceSettings({
    sourceName: 'browser',
    sourceSettings: {
      url: value,
    }
  });
  return await show('browser');
}

async function updateText(id, value) {
  return await obs.SetSourceSettings({
    sourceName: id,
    sourceSettings: {
      text: value
    }
  });
}

async function setText(value) {
  await obs.SetSourceSettings({
    sourceName: 'text1',
    sourceSettings: {
      text: value
    }
  });
  return await show('text1');
}

async function setShowTitle(value) {
  await updateText('title', value);
  return true;
}

async function updateImage(id, filename) {
  return await obs.SetSourceSettings({
    sourceName: id,
    sourceSettings: {
      file: filename
    }
  });
}

async function setImage(filename) {
  await obs.SetSourceSettings({
    sourceName: 'image',
    sourceSettings: {
      file: filename
    }
  });
  return await show('image');
}

//166x126
//
async function position(id, x = 0, y = 0, w = 1, h = 1, rotation = 0) {
  return await obs.SetSceneItemProperties({
    item: id,
    position: {
      x: x,
      y: y,
      rotation: rotation
    },
    scale: {
      x: w,
      y: h
    }
  });
}

async function hide(id, scene='main') {
  try {
    let response = await obs.SetSceneItemProperties({
      // scene: scene,
      item: id,
      visible: false
    });
    return response;
  } catch (e) {
    console.log(e);
    return e;
  }
}

async function show(id, scene='main') {
  try {
    let response = await obs.SetSceneItemProperties({
      // scene: scene,
      item: id,
      visible: true
    });
    return response;
  } catch (e) {
    console.log(e);
    return e;
  }
}

async function showAll() {
  for (let i = 0; i < SOURCES.length; i++) {
    await show(SOURCES[i])
  }
  return true;
}

async function hideAll() {
  for (let i = 0; i < SOURCES.length; i++) {
    await hide(SOURCES[i]);
  }
  return true;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function natureShow() {
  cleanup();
  await setShowTitle('NATURE\nSHOW');
  await setRemoteURL('');
  await sleep(1000);
  await setRemoteURL('http://159.65.190.4:8089');
  return true
}

async function copShow() {
  cleanup();
  await setShowTitle('COP\nSHOW');
  await setRemoteURL('');
  await setAudio(`${BASE}/copshow/cops.mp3`);
  let url = await createWebServer(`${BASE}/copshow`);
  await sleep(1000);
  await setRemoteURL(url);
  // await sleep(500);
  // await hide('browser');
  // await sleep(500);
  // await show('browser');
  return true;
}

async function meditationShow() {
  cleanup();
  setShowTitle('MEDITATION\nSHOW');
  show('window');

  p = `${BASE}/meditationshow/meditationshow`;

  let child = spawn(p);

  child.stdout.on('data', (data) => {
    console.log(''+data);
  });

  child.stderr.on('data', (data) => {
    console.error(`child stderr:\n${data}`);
  });
}

async function tipsShow() {
  cleanup();
  await setShowTitle('ADVICE\nSHOW');
  await setRemoteURL('');
  await sleep(1000);
  await setRemoteURL('http://reallycool.tips');
  // await sleep(500);
  // await hide('browser');
  // await sleep(500);
  // await show('browser');
}

async function cookingShow() {
  cleanup();
  setShowTitle('COOKING\nSHOW');
  setVideo(`${BASE}/cookingshow2/cookingshow.mp4`);
}

async function homeInvaderShow() {
  cleanup();
  setShowTitle('HOME\nSHOW');
  let txt = fs.readFileSync(`${BASE}/homeshow/the_apartment.txt`, 'utf-8');
  // txt = txt.replace('\n', '       *       ', 'g');
  // updateText('bottom_text', txt);
  let txts = txt.split('\n');
  random.shuffle(txts);
  let i = 0;
  timeout = setInterval(function() {
    setText(txts[i].trim());
    i++;
    if (i >= txts.length) i = 0;
  }, 7000);
  setVideo(`${BASE}/homeshow/home_invader.mp4`);
}

async function laborShow() {
  cleanup();

  setShowTitle('SHOPPING\nSHOW');
  setAudio(`${BASE}/shoppingshow/Split_Phase_-_24_-_Tuesdays_Groove.mp3`);

  let urls = fs.readFileSync(`${BASE}/shoppingshow/shoppinglist.txt`, 'utf-8').split('\n');
  random.shuffle(urls);
  await setRemoteURL('');
  await sleep(1000);
  await setRemoteURL(urls[0].trim());
  // await sleep(500);
  // await hide('browser');
  // await sleep(500);
  // await show('browser');
  let urlTime = 12000;
  let i = 1;
  timeout = setInterval(function() {
    console.log(urls[i]);
    setRemoteURL(urls[i].trim());
    i++;
    if (i >= urls.length) i = 0;
  }, urlTime);
}

async function resetLogo() {
  updateImage('logo', `${BASE}/autotv/assets/logo.png`);
}

async function randomLogo() {
  let png = ('' + random.integer(0, 157)).padStart(4, '0');
  let filename = `${BASE}/autotv/assets/logos/${png}.png`;
  console.log(filename);
  updateImage('logo', filename);
  position('logo', 1270, 10, 0.3, 0.3);
  setTimeout(randomLogo, 1000);
}

async function printSourceInfo() {
  let sourcelist = await obs.GetSourcesList();

  for (source of sourcelist.sources) {
    console.log(source);
    let info = await obs.GetSourceSettings({
      sourceName: source.name
    });
    console.log(info);
  }
}

async function getCurrentShow() {
  let data = await readFile('../docs/schedule.json', 'utf8');
  let schedule = JSON.parse(data);

  let currentTime = moment().tz('America/New_York');

  let show = schedule[schedule.length - 1];

  for (let i = 0; i < schedule.length - 1; i++) {
    let ts = moment(schedule[i].time, 'HH:mm:ss').tz('America/New_York');
    let nextTs = moment(schedule[i+1].time, 'HH:mm:ss').tz('America/New_York');

    if (currentTime.isSameOrAfter(ts) && currentTime.isBefore(nextTs)){
      show = schedule[i]
    }
  }

  return show;
}

async function switchShows(show) {
  if (!show) show = await getCurrentShow();

  if (show.program != currentShow && showCodes[show.program]) {
    currentShow = show.program;
    await hideAll();
    await switchScene('transition');
    await updateText('nextshow', currentShow.toUpperCase());
    console.log(`switching to ${currentShow}`);
    await sleep(5000);
    await switchScene('main');
    await sleep(500);
    showCodes[show.program]();
  }
}

async function main() {
  try {
    obs.onSwitchScenes(data => {
      console.log(`New Active Scene: ${data.sceneName}`);
    });

    obs.on('error', err => {
      console.error('socket error:', err);
    });

    await obs.connect({address: HOST, password: PASS});
    // await switchScene('main');
    // await printSourceInfo();
    console.log('Connected!');
    // await show('transition');
    // switchShows({program: 'Cop Show'})
    // switchShows({program: 'Advice Show'})
    switchShows();
    setInterval(switchShows, 10*1000);

  } catch (e) {
    console.log(e);
  }
}

main();
