var CACHE_VERSION = 'v8';
var CACHE_NAME = 'midi-real-book-' + CACHE_VERSION;

var URLS_TO_CACHE = [
  '/',
  '/site.css',
  '/site.js',
  '/manifest.json',
  '/ensembles/index.html',
  '/ensembles/abstract-fusion.html',
  '/ensembles/ac-dc.html',
  '/ensembles/aerosmith.html',
  '/ensembles/allan-holdsworth-band.html',
  '/ensembles/andy-timmons-orbit.html',
  '/ensembles/animals-as-leaders.html',
  '/ensembles/austin-melodic-blues.html',
  '/ensembles/beatles.html',
  '/ensembles/billy-idol.html',
  '/ensembles/black-sabbath.html',
  '/ensembles/blt.html',
  '/ensembles/blues-metal.html',
  '/ensembles/blues-rock-shred.html',
  '/ensembles/brothers-johnson-quincy-jones.html',
  '/ensembles/bruford-uk.html',
  '/ensembles/buckethead-bozzio-orbit.html',
  '/ensembles/buckethead-primus-orbit.html',
  '/ensembles/cab.html',
  '/ensembles/chic.html',
  '/ensembles/cream.html',
  '/ensembles/dave-weckl-band-grp.html',
  '/ensembles/david-lee-roth-band.html',
  '/ensembles/deep-purple.html',
  '/ensembles/dokken.html',
  '/ensembles/dream-theater.html',
  '/ensembles/duke-ellington-orchestra.html',
  '/ensembles/earth-wind-and-fire.html',
  '/ensembles/electric-fusion-circuit.html',
  '/ensembles/electric-light-orchestra.html',
  '/ensembles/europe.html',
  '/ensembles/extreme.html',
  '/ensembles/fourplay.html',
  '/ensembles/frank-zappa-band.html',
  '/ensembles/funk-fusion-session.html',
  '/ensembles/fusion-shred-circuit.html',
  '/ensembles/genesis.html',
  '/ensembles/hard-bop-blues.html',
  '/ensembles/helloween-power-metal.html',
  '/ensembles/intervals.html',
  '/ensembles/iron-maiden.html',
  '/ensembles/jack-bruce-gary-moore-band.html',
  '/ensembles/james-brown-funk.html',
  '/ensembles/jazz-funk-fusion.html',
  '/ensembles/jeff-beck.html',
  '/ensembles/jimi-hendrix-experience.html',
  '/ensembles/joe-satriani-band.html',
  '/ensembles/john-mayer-trio.html',
  '/ensembles/journey.html',
  '/ensembles/king-crimson.html',
  '/ensembles/king-curtis-aretha.html',
  '/ensembles/king-s-x.html',
  '/ensembles/kiss.html',
  '/ensembles/l-a-fusion-session.html',
  '/ensembles/l-a-jazz-session.html',
  '/ensembles/l-a-session-fusion-rock.html',
  '/ensembles/led-zeppelin.html',
  '/ensembles/lee-ritenour-band.html',
  '/ensembles/liquid-tension-experiment.html',
  '/ensembles/living-colour.html',
  '/ensembles/mahavishnu-fusion.html',
  '/ensembles/mahavishnu-shakti.html',
  '/ensembles/marcus-miller-band.html',
  '/ensembles/mclaughlin-hellborg-orbit.html',
  '/ensembles/meshuggah-periphery.html',
  '/ensembles/metal-shred.html',
  '/ensembles/metallica.html',
  '/ensembles/michael-jackson-session-orbit.html',
  '/ensembles/michel-camilo-steve-khan-orbit.html',
  '/ensembles/miles-davis-hard-bop-orbit.html',
  '/ensembles/miles-davis-sting-fusion.html',
  '/ensembles/mingus-bands.html',
  '/ensembles/modal-jazz-reinterpretation.html',
  '/ensembles/modern-blues-rock.html',
  '/ensembles/modern-funk-rhythm.html',
  '/ensembles/modern-fusion-dialogue.html',
  '/ensembles/modern-fusion-virtuoso.html',
  '/ensembles/modern-neo-soul.html',
  '/ensembles/motown.html',
  '/ensembles/mr-big.html',
  '/ensembles/neoclassical-shred.html',
  '/ensembles/one-hot-minute.html',
  '/ensembles/oscar-peterson-ray-brown.html',
  '/ensembles/ozzy-osbourne.html',
  '/ensembles/p-funk-buckethead.html',
  '/ensembles/parliament-funkadelic.html',
  '/ensembles/pat-metheny-group.html',
  '/ensembles/peter-gabriel.html',
  '/ensembles/pink-floyd.html',
  '/ensembles/planet-x.html',
  '/ensembles/plini.html',
  '/ensembles/polyphia.html',
  '/ensembles/primus.html',
  '/ensembles/queen.html',
  '/ensembles/rainbow.html',
  '/ensembles/red-hot-chili-peppers.html',
  '/ensembles/return-to-forever.html',
  '/ensembles/robben-ford-band.html',
  '/ensembles/rush.html',
  '/ensembles/santana.html',
  '/ensembles/scorpions.html',
  '/ensembles/shrapnel-shred.html',
  '/ensembles/sly-and-the-family-stone.html',
  '/ensembles/stax.html',
  '/ensembles/steve-morse-band.html',
  '/ensembles/stevie-ray-vaughan-double-trouble.html',
  '/ensembles/stevie-wonder.html',
  '/ensembles/studio-groove.html',
  '/ensembles/swing-guitar.html',
  '/ensembles/the-aristocrats.html',
  '/ensembles/thelonious-monk-quartet.html',
  '/ensembles/the-meters.html',
  '/ensembles/the-police.html',
  '/ensembles/the-who.html',
  '/ensembles/the-winery-dogs.html',
  '/ensembles/thrash-metal-lead.html',
  '/ensembles/tool.html',
  '/ensembles/toto.html',
  '/ensembles/tribal-tech.html',
  '/ensembles/ufo.html',
  '/ensembles/uzeb-fusion.html',
  '/ensembles/van-halen.html',
  '/ensembles/whitesnake.html',
  '/ensembles/winger.html',
  '/ensembles/wrecking-crew.html',
  '/ensembles/yellowjackets-blues-fusion.html',
  '/ensembles/yes.html',
  '/ensembles/yngwie-malmsteen.html',
  '/ensembles/zz-top.html'
];

self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      return cache.addAll(URLS_TO_CACHE);
    })
  );
});

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys
          .filter(function (key) {
            return key.startsWith('midi-real-book-') && key !== CACHE_NAME;
          })
          .map(function (key) { return caches.delete(key); })
      );
    }).then(function () {
      return self.clients.claim();
    })
  );
});

self.addEventListener('fetch', function (event) {
  event.respondWith(
    caches.match(event.request).then(function (cached) {
      return cached || fetch(event.request);
    })
  );
});
