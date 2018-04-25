const fs = require('fs');
const spawn = require('child_process').spawn;
const OBSWebSocket = require('obs-websocket-js');
const obs = new OBSWebSocket();
let random = require('random-js')();

const HOST = 'localhost:4444';
const PASS = 'autotv';
const BASE = '/Users/sam/autotv';

let timeout;


async function cleanup() {
  clearTimeout(timeout);
  spawn('killall', ['-9', 'pelosi']);
}

async function switchTo(name, transition = 'Fade', duration = 1000) {
  await obs.SetCurrentScene({'scene-name': name});
  return true;
}

async function updateVideo(id, filename) {
  obs.SetSourceSettings({
    sourceName: id,
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

async function updateText(id, value) {
  obs.SetSourceSettings({
    sourceName: id,
    sourceSettings: {
      text: value
    }
  });
}

async function changeImage(id, filename) {
  return await obs.SetSourceSettings({
    sourceName: id,
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

async function hide(id) {}

async function show(id) {}

async function copShow() {
  cleanup();
  await switchTo('coptv');
}

async function meditationShow() {
  cleanup();
  setTimeout(() => {
    let pelosi = `${BASE}/meditationshow/bin/pelosi.app/Contents/MacOS/pelosi`;
    spawn(pelosi);
    switchTo('meditationtv');
  }, 5000);
}

async function tipsShow() {
  cleanup();
  await switchTo('tipstv');
}

async function cookingShow() {
  cleanup();
  await switchTo('cookingtv');
  updateVideo('cookingvideo', `none`);
  setTimeout(function(){
    updateVideo('cookingvideo', `${BASE}/cookingshow2/cookingshow.mp4`);
  }, 1000);
}

async function homeInvaderShow() {
  cleanup();
  switchTo('hometv');
  let txt = fs.readFileSync(`${BASE}/homeshow/the_apartment.txt`, 'utf-8');
  // txt = txt.replace('\n', '       *       ', 'g');
  // updateText('bottom_text', txt);
  let txts = txt.split('\n');
  random.shuffle(txts);
  let i = 0;
  timeout = setInterval(function() {
    updateText('bottom_text', txts[i].trim());
    i++;
    if (i >= txts.length) i = 0;
  }, 7000);
  updateVideo('homevideo', `none`);
  setTimeout(function(){
    updateVideo('homevideo', `${BASE}/homeshow/home_invader.mp4`);
  }, 1000);
}

async function laborShow() {
  cleanup();
  switchTo('refuge');
  let urls = fs.readFileSync(`${BASE}/shoppingshow/shoppinglist.txt`, 'utf-8').split('\n');
  random.shuffle(urls);
  // let urlTime = Math.floor(60*60*1000/urls.length);
  let urlTime = 12000;
  console.log('url time', urlTime);
  let i = 0;
  timeout = setInterval(function() {
    updateURL('alibaba', urls[i].trim());
    console.log(urls[i]);
    i++;
    if (i >= urls.length) i = 0;
  }, urlTime);
}

async function resetLogo() {
  changeImage('logo', `${BASE}/autotv/assets/logo.png`);
}

async function randomLogo() {
  let png = ('' + random.integer(0, 157)).padStart(4, '0');
  let filename = `${BASE}/autotv/assets/logos/${png}.png`;
  console.log(filename);
  changeImage('logo', filename);
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

    // await switchTo('empty');

    //await printSourceInfo();

    let allshows = [meditationShow, copShow, homeInvaderShow, laborShow, cookingShow, tipsShow];
    let showIndex = 0;

    allshows[showIndex]();
    setInterval(() => {
      showIndex ++;
      if (showIndex >= allshows.length) showIndex = 0;
      allshows[showIndex]();
    }, 60*60*1000);

    // resetLogo();

    // let sceneData = await obs.getSceneList();
    // let sourcelist = await obs.GetSourcesList();
    // randomLogo();

  } catch (e) {
    console.log(e);
  }
}

main();
