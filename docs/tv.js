function addShadows(el) {
  // let shadows = [];
  // let total = 8;
  // for (var i = 0; i < total; i++) {
  //   let offset = i * 10;
  //   let c = (total - i) / total * 255;
  //   shadows.push(`${0}px ${0}px 0px ${offset}px hsla(${c}, 100%, 50%, 0.4)`);
  // }
  // el.style.boxShadow = shadows.join(',');
  //

  let shadows = [];
  let total = 190;
  for (var i = 0; i < total; i++) {
    let offset = i * 10;
    let c = offset * 0.4; //(total - i) / total * 255;
    shadows.push(`${offset}px ${offset}px 0px hsla(${c}, 100%, 50%, 0.3)`);
  }
  el.style.boxShadow = shadows.join(',');
}

function addSchedule(schedule) {
  let today = moment().format('MMMM Do YYYY');
  document.querySelector('#today').textContent = today;
  let elements = schedule.map(s => {
    let ts = moment(s.time, 'HH:mm:ss').tz('America/New_York');
    return `
      <div class="schedule-item" data-time="${ts}">
        <span class="time hl blue">${ts.format('HH:mm:ss z')}</span>
        <span class="show hl red">${s.program}</span>
      </div>
    `;
  });
  document.querySelector('#schedule-items').innerHTML = elements.join('');
}

function checkSchedule() {
  let items = document.querySelectorAll('.schedule-item');
  for (let i = 0; i < items.length; i++) {
    let item = items[i];
    let ts = item.getAttribute('data-time');

  }
}

fetch('schedule.json')
  .then(function(response) {
    return response.json();
  })
  .then(addSchedule);

// let watch =
// document.querySelectorAll('
addShadows(document.querySelector('.watch'));
