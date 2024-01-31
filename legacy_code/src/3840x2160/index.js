const API_URL = "https://calendar.library.ucla.edu/widget/hours/grid?";

const locationIds = {
  powLab: 2609,
  powLend: 2608,
  yrlLend: 2614,
  powClass: 2607,
};
const numWeeks = 2;
const format = "json";

function render(weekdays) {
  // render the date range
  const start = weekdays[0].date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
  });
  const end = weekdays.at(-1).date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
  });
  document.querySelector("h2").textContent = `${start} - ${end}`;

  // render the table
  const [leftContainer, rightContainer] = document.querySelectorAll("ul");
  weekdays.forEach((item, index) => {
    const li = document.createElement("li");
    const daySpan = document.createElement("span");
    daySpan.textContent = item.date.toLocaleString("en-US", {
      weekday: "long",
    });
    daySpan.classList.add("day");
    const timeSpan = document.createElement("span");
    timeSpan.textContent = item.rendered;
    timeSpan.classList.add("time");
    li.append(daySpan, timeSpan);
    if (index < 4) leftContainer.append(li);
    else rightContainer.append(li);
    if (item.date.getDate() === new Date().getDate()) li.classList.add("today");
  });
}

fetch(
  API_URL +
    new URLSearchParams({
      lid: locationIds.powLab,
      weeks: numWeeks,
      format: format,
    })
)
  .then((res) => res.json())
  .then((res) => {
    let weekdays = [
      ...Object.values(Object.values(res)[0].weeks[0]),
      ...Object.values(Object.values(res)[0].weeks[1]),
    ];
    weekdays = weekdays
      .slice(1, 8)
      .map(({ date, ...item }) => ({
        date: new Date(`${date}GMT-0700`),
        ...item,
      }))
      .sort((a, b) => a.date - b.date);
    render(weekdays);
  });
