new gridjs.Grid({
  columns: ['Feed', 'Subscribers'],
  server: {
    url: 'http://185.189.167.178/bulk/zen_feeds?limit=50',
    then: data => data.map(item => [item._id, item.feed_subscribers])
  }
}).render(document.getElementById("wrapper"));
