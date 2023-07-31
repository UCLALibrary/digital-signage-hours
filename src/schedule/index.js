const TOKEN_URL = "https://calendar.library.ucla.edu/1.1/oauth/token";
const EVENT_URL = "https://calendar.library.ucla.edu/1.1/events?";
const HOUR_URL = "https://calendar.library.ucla.edu/1.1/hours/";

// Private constants
const client_id = "1301";
const client_secret = ""; // insert your client secret here

// Public constants
const calendarIds = {
  classA: 3363,
  classB: 4357,
  classC: 4358,
  inq3: 4799,
};
const days = 0;
const limit = 100;
const locationId = 2609;
const wordLimit = 40;
const now = new Date();

// Styling constants
const gridHeight = 100;
const headHeight = 92;

async function getData() {
  // get access token
  const res = await fetch(TOKEN_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      client_id,
      client_secret,
      grant_type: "client_credentials",
    }),
  });
  const { access_token } = await res.json();

  // get events
  const eventDict = {};
  const eventPromises = [];
  const hourDict = {
    status: "closed",
  };

  for (const [location, cal_id] of Object.entries(calendarIds)) {
    const eventPromise = fetch(
      EVENT_URL +
        new URLSearchParams({
          cal_id,
          days,
          limit,
        }),
      {
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      }
    )
      .then((res) => {
        if (res.ok) return res.json();
      })
      .then(({ events }) => {
        events = events.map((event) => ({
          title: event.title,
          start: new Date(event.start),
          end: new Date(event.end),
        }));
        eventDict[location] = events;
      })
      .catch((err) => {
        console.error(err);
      });
    eventPromises.push(eventPromise);
  }

  // get opening hour
  const hourPromise = fetch(HOUR_URL + locationId, {
    headers: {
      Authorization: `Bearer ${access_token}`,
    },
  })
    .then((res) => {
      if (res.status === 200) return res.json();
      else return null;
    })
    .then((res) => {
      const [date, hour] = Object.entries(res[0].dates)[0];
      hourDict.status = hour.status;

      // convert time string
      function convertTime(date, time) {
        let [hour, rest] = time.split(":");
        const minute = rest.slice(0, 2);
        const ampm = rest.slice(-2);
        hour =
          ampm === "am" ? ("00" + hour).slice(-2) : (+hour + 12).toString();
        return new Date(date + "T" + hour + ":" + minute + ":00-07:00");
      }

      if (hour.status === "open") {
        hourDict.start = convertTime(date, hour.hours[0].from);
        hourDict.end = convertTime(date, hour.hours[0].to);
      }
    });
  eventPromises.push(hourPromise);

  await Promise.all(eventPromises);
  return [eventDict, hourDict];
}

function render(eventDict, hourDict) {
  // update now pointer
  const pointNow = document.querySelector(".now");
  function updateNow() {
    const now = new Date();
    pointNow.style.top =
      Math.floor(now.getHours() - 8) * gridHeight +
      (now.getMinutes() / 60) * gridHeight +
      headHeight +
      "px";
  }
  updateNow();
  pointNow.style.display = "block";
  setInterval(updateNow, 60000);

  // render opening hour
  const locBgs = document.querySelectorAll(".loc-bg");
  const msg = document.querySelector(".msg");
  msg.style.visibility = "visible";

  if (hourDict.status === "open") {
    const start = hourDict.start.getHours() - 6;
    const end = hourDict.end.getHours() - 6;
    locBgs.forEach((locBg) => {
      locBg.style.display = "block";
      locBg.style.gridRow = `${start} / ${end}`;
    });
    msg.textContent = "* White space = open for drop-in study.";
  } else {
    locBgs.forEach((locBg) => {
      locBg.style.display = "block";
      locBg.style.height = "0";
    });
  }

  // render events
  function truncate(str, n) {
    return str.length > n ? str.slice(0, n - 1) + "&hellip;" : str;
  }

  for (const [location, events] of Object.entries(eventDict)) {
    const loc = document.querySelector(`.loc-bg.${location}`);
    if (events.length) {
      events.forEach((event) => {
        const eventDiv = document.createElement("div");
        eventDiv.classList.add("event");
        eventDiv.style.top =
          Math.floor(
            event.start.getHours() - (hourDict.start?.getHours() ?? 9)
          ) *
            gridHeight +
          (event.start.getMinutes() / 60) * gridHeight +
          "px";
        eventDiv.style.height =
          Math.floor((event.end - event.start) / 1000 / 60 / 60) * gridHeight +
          "px";
        eventDiv.innerHTML = truncate(event.title, wordLimit);
        loc.appendChild(eventDiv);
      });
    }
  }
}

if (now.getHours() >= 8 && now.getHours() <= 20) {
  getData().then(([eventDict, hourDict]) => render(eventDict, hourDict));
}
