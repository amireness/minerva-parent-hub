const destinations = new Map([
  ['#application', '?topic=understand'],
  ['#parent-involvement', '?topic=parent'],
  ['#aid-preparation', '/financial-aid'],
  ['#planning', '/deadlines'],
  ['#support', '/help'],
]);
const destination = destinations.get(location.hash);
if (destination) location.replace(destination);
