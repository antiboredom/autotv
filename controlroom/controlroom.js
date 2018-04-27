const fs = require('fs');
const spawn = require('child_process').spawn;
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
  obs.SetSourceSettings({
    sourceName: id,
    sourceSettings: {
      local_file: filename
    }
  });
}

async function setVideo(filename){
  show('video');
  obs.SetSourceSettings({
    sourceName: 'video',
    sourceSettings: {
      local_file: filename
    }
  });
}

async function setAudio(filename){
  show('audio1');
  obs.SetSourceSettings({
    sourceName: 'audio1',
    sourceSettings: {
      local_file: filename
    }
  });
}

async function setAudio2(filename){
  show('audio2');
  obs.SetSourceSettings({
    sourceName: 'audio2',
    sourceSettings: {
      local_file: filename
    }
  });
}

async function updateURL(id, value) {
  obs.SetSourceSettings({
    sourceName: id,
    sourceSettings: {
      url: value
    }
  });
}

async function setLocalURL(value) {
  obs.ResetSceneItem({'scene-name': 'main', item: 'browser'});
  show('browser');
  obs.SetSourceSettings({
    sourceName: 'browser',
    sourceSettings: {
      local_file: value
    }
  });
}

async function setRemoteURL(value) {
  obs.ResetSceneItem({'scene-name': 'main', item: 'browser'});
  show('browser');
  obs.SetSourceSettings({
    sourceName: 'browser',
    sourceSettings: {
      url: value,
    }
  });
}

async function updateText(id, value) {
  obs.SetSourceSettings({
    sourceName: id,
    sourceSettings: {
      text: value
    }
  });
}

async function setText(value) {
  show('text1');
  obs.SetSourceSettings({
    sourceName: 'text1',
    sourceSettings: {
      text: value
    }
  });
}

async function setShowTitle(value) {
  updateText('title', value);
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
  show('image');
  return await obs.SetSourceSettings({
    sourceName: 'image',
    sourceSettings: {
      file: filename
    }
  });
}

//166x126
//
async function position(id, x = 0, y = 0, w = 1, h = 1, rotation = 0) {
  obs.SetSceneItemProperties({
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

async function hide(id) {
  obs.SetSceneItemProperties({
    item: id,
    visible: false
  });
}

async function show(id) {
  obs.SetSceneItemProperties({
    item: id,
    visible: true
  });
}

async function showAll() {
  SOURCES.forEach(show);
}

async function hideAll() {
  SOURCES.forEach(hide);
}

function switchShow(showName) {
  cleanup()
}

async function copShow() {
  cleanup();
  setShowTitle('COP\nSHOW');
  setAudio(`${BASE}/copshow/cops.mp3`);
  let url = await createWebServer(`${BASE}/copshow`);
  console.log(url);
  setRemoteURL(url);
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
  setShowTitle('ADVICE\nSHOW');
  setRemoteURL('http://reallycool.tips');
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
  setRemoteURL(urls[0].trim());
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

async function main() {
  try {
    obs.onSwitchScenes(data => {
      console.log(`New Active Scene: ${data.sceneName}`);
    });

    obs.on('error', err => {
      console.error('socket error:', err);
    });

    await obs.connect({address: HOST, password: PASS});
    console.log('Connected!');

    let allshows = [cookingShow, copShow, tipsShow, laborShow, homeInvaderShow, meditationShow];
    let index = 0;
    hideAll();
    copShow()
    // setInterval(() => {
    //   hideAll();
    //   allshows[index]();
    //   index ++;
    //   if (index > allshows.length - 1) index = 0;
    // }, 10000);

    // await printSourceInfo();

  } catch (e) {
    console.log(e);
  }
}

main();
