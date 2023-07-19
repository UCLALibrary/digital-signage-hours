const TOKEN_URL = "https://calendar.library.ucla.edu/1.1/oauth/token";
const API_URL = "https://calendar.library.ucla.edu/1.1/events?";

// Private constants
const client_id = "1301";
const client_secret = "cfe807acd139881549ca6a11f468c199";

// Public constants
const locationIds = {
  classA: 3363,
  classB: 4357,
  classC: 4358,
  inq3: 4799,
};
const days = 0;
const limit = 100;

async function getEvents() {
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
  for (const [location, cal_id] of Object.entries(locationIds)) {
    const eventPromise = fetch(
      API_URL +
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
        if (res.status === 200) return res.json();
        else return null;
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
        return null;
      });
    eventPromises.push(eventPromise);
  }

  await Promise.all(eventPromises);
  return eventDict;
}

function render(eventDict) {
  console.log(eventDict);
}

getEvents().then((eventDict) => render(eventDict));
