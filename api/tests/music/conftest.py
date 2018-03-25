import pytest


_artists = {'search': {}, 'get': {}}

_artists['search']['adhesive_wombat'] = {
    'artist-list': [
        {
            'type': 'Person',
            'ext:score': '100',
            'id': '62c3befb-6366-4585-b256-809472333801',
            'disambiguation': 'George Shaw',
            'gender': 'male',
            'area': {'sort-name': 'Raleigh', 'id': '3f8828b9-ba93-4604-9b92-1f616fa1abd1', 'name': 'Raleigh'},
            'sort-name': 'Wombat, Adhesive',
            'life-span': {'ended': 'false'},
            'name': 'Adhesive Wombat'
        },
        {
            'country': 'SE',
            'type': 'Group',
            'ext:score': '42',
            'id': '61b34e69-7573-4208-bc89-7061bca5a8fc',
            'area': {'sort-name': 'Sweden', 'id': '23d10872-f5ae-3f0c-bf55-332788a16ecb', 'name': 'Sweden'},
            'sort-name': 'Adhesive',
            'life-span': {'end': '2002-07-12', 'begin': '1994', 'ended': 'true'},
            'name': 'Adhesive',
            'begin-area': {
                'sort-name': 'Katrineholm',
                'id': '02390d96-b5a3-4282-a38f-e64a95d08b7f',
                'name': 'Katrineholm'
            },
        },
    ]
}
_artists['get']['adhesive_wombat'] = {'artist': _artists['search']['adhesive_wombat']['artist-list'][0]}

_artists['get']['soad'] = {
    'artist': {
        'country': 'US',
        'isni-list': ['0000000121055332'],
        'type': 'Group',
        'area': {
            'iso-3166-1-code-list': ['US'],
            'sort-name': 'United States',
            'id': '489ce91b-6658-3307-9877-795b68554c98',
            'name': 'United States'
        },
        'begin-area': {
            'sort-name': 'Glendale',
            'id': '6db2e45d-d7f3-43da-ac0b-7ba5ca627373',
            'name': 'Glendale'
        },
        'id': 'cc0b7089-c08d-4c10-b6b0-873582c17fd6',
        'life-span': {'begin': '1994'},
        'sort-name': 'System of a Down',
        'name': 'System of a Down'
    }
}

_albums = {'search': {}, 'get': {}, 'get_with_includes': {}}
_albums['search']['hypnotize'] = {
    'release-list': [
        {
            "artist-credit": [
                {
                    "artist": {
                        "alias-list": [
                            {
                                "alias": "SoaD",
                                "sort-name": "SoaD",
                                "type": "Search hint"
                            },
                            {
                                "alias": "S.O.A.D.",
                                "sort-name": "S.O.A.D.",
                                "type": "Search hint"
                            },
                            {
                                "alias": "System Of Down",
                                "sort-name": "System Of Down",
                                "type": "Search hint"
                            }
                        ],
                        "id": "cc0b7089-c08d-4c10-b6b0-873582c17fd6",
                        "name": "System of a Down",
                        "sort-name": "System of a Down"
                    }
                }
            ],
            "artist-credit-phrase": "System of a Down",
            "barcode": "",
            "country": "US",
            "date": "2005",
            "ext:score": "100",
            "id": "47ae093f-1607-49a3-be11-a15d335ccc94",
            "label-info-list": [
                {
                    "catalog-number": "8-2796-93871-2",
                    "label": {
                        "id": "f5be9cfe-e1af-405c-a074-caeaed6797c0",
                        "name": "American Recordings"
                    }
                },
                {
                    "catalog-number": "D162990",
                    "label": {
                        "id": "9a7d39a4-a887-40f3-a645-a9a136d1f13f",
                        "name": "BMG Direct Marketing, Inc."
                    }
                }
            ],
            "medium-count": 1,
            "medium-list": [
                {
                    "disc-count": 1,
                    "disc-list": [],
                    "format": "CD",
                    "track-count": 12,
                    "track-list": []
                }
            ],
            "medium-track-count": 12,
            "packaging": "Digipak",
            "release-event-list": [
                {
                    "area": {
                        "id": "489ce91b-6658-3307-9877-795b68554c98",
                        "iso-3166-1-code-list": [
                            "US"
                        ],
                        "name": "United States",
                        "sort-name": "United States"
                    },
                    "date": "2005"
                }
            ],
            "release-group": {
                "id": "72035143-d6ec-308b-8ee5-070b8703902a",
                "primary-type": "Album",
                "type": "Album"
            },
            "status": "Official",
            "text-representation": {
                "language": "eng",
                "script": "Latn"
            },
            "title": "Hypnotize"
        },
        {
            "artist-credit": [
                {
                    "artist": {
                        "alias-list": [
                            {
                                "alias": "SoaD",
                                "sort-name": "SoaD",
                                "type": "Search hint"
                            },
                            {
                                "alias": "S.O.A.D.",
                                "sort-name": "S.O.A.D.",
                                "type": "Search hint"
                            },
                            {
                                "alias": "System Of Down",
                                "sort-name": "System Of Down",
                                "type": "Search hint"
                            }
                        ],
                        "id": "cc0b7089-c08d-4c10-b6b0-873582c17fd6",
                        "name": "System of a Down",
                        "sort-name": "System of a Down"
                    }
                }
            ],
            "artist-credit-phrase": "System of a Down",
            "asin": "B000C6NRY8",
            "barcode": "827969387115",
            "country": "US",
            "date": "2005-12-20",
            "ext:score": "100",
            "id": "8a4034a9-7834-3b7e-a6f0-d0791e3731fb",
            "medium-count": 1,
            "medium-list": [
                {
                    "disc-count": 0,
                    "disc-list": [],
                    "format": "Vinyl",
                    "track-count": 12,
                    "track-list": []
                }
            ],
            "medium-track-count": 12,
            "release-event-list": [
                {
                    "area": {
                        "id": "489ce91b-6658-3307-9877-795b68554c98",
                        "iso-3166-1-code-list": [
                            "US"
                        ],
                        "name": "United States",
                        "sort-name": "United States"
                    },
                    "date": "2005-12-20"
                }
            ],
            "release-group": {
                "id": "72035143-d6ec-308b-8ee5-070b8703902a",
                "primary-type": "Album",
                "type": "Album"
            },
            "status": "Official",
            "text-representation": {
                "language": "eng",
                "script": "Latn"
            },
            "title": "Hypnotize"
        },
    ]
}
_albums['get']['hypnotize'] = {'release': _albums['search']['hypnotize']['release-list'][0]}
_albums['get_with_includes']['hypnotize'] = {
  'release': {
    'artist-credit': [
        {'artist': {'id': 'cc0b7089-c08d-4c10-b6b0-873582c17fd6',
            'name': 'System of a Down',
            'sort-name': 'System of a Down'}}],
  'artist-credit-phrase': 'System of a Down',
  'barcode': '',
  'country': 'US',
  'cover-art-archive': {'artwork': 'true',
   'back': 'false',
   'count': '1',
   'front': 'true'},
  'date': '2005',
  'id': '47ae093f-1607-49a3-be11-a15d335ccc94',
  'medium-count': 1,
  'medium-list': [{'format': 'CD',
    'position': '1',
    'track-count': 12,
    'track-list': [{'id': '59f5cf9a-75b2-3aa3-abda-6807a87107b3',
      'length': '186000',
      'number': '1',
      'position': '1',
      'recording': {'id': '76d03fc5-758c-48d0-a354-a67de086cc68',
       'length': '186000',
       'title': 'Attack'},
      'track_or_recording_length': '186000'},
     {'id': '3aaa28c1-12b1-3c2a-b90a-82e09e355608',
      'length': '239000',
      'number': '2',
      'position': '2',
      'recording': {'id': '327543b0-9193-48c5-83c9-01c7b36c8c0a',
       'length': '239000',
       'title': 'Dreaming'},
      'track_or_recording_length': '239000'},
     {'id': 'a34fef19-e637-3436-b7eb-276ff2814d6f',
      'length': '147000',
      'number': '3',
      'position': '3',
      'recording': {'id': '6e27866c-07a1-425d-bb4f-9d9e728db344',
       'length': '147000',
       'title': 'Kill Rock ’n Roll'},
      'track_or_recording_length': '147000'},
     {'id': '72a4e5c0-c150-3ba1-9ceb-3ab82648af25',
      'length': '189000',
      'number': '4',
      'position': '4',
      'recording': {'id': '7ff8a67d-c8e2-4b3a-a045-7ad3561d0605',
       'length': '189000',
       'title': 'Hypnotize'},
      'track_or_recording_length': '189000'},
     {'id': 'a748fa6e-b3b7-3b22-89fb-a038ec92ac32',
      'length': '178000',
      'number': '5',
      'position': '5',
      'recording': {'id': '19b6eb6a-0e76-4ef7-b63f-959339dbd5d2',
       'length': '178000',
       'title': 'Stealing Society'},
      'track_or_recording_length': '178000'},
     {'id': '5c5a8d4e-e21a-317e-a719-6e2dbdefa5d2',
      'length': '216000',
      'number': '6',
      'position': '6',
      'recording': {'id': 'c3c2afe1-ee9a-47cb-b3c6-ff8100bc19d5',
       'length': '216000',
       'title': 'Tentative'},
      'track_or_recording_length': '216000'},
     {'id': '265718ba-787f-3193-947b-3b6fa69ffe96',
      'length': '175000',
      'number': '7',
      'position': '7',
      'recording': {'id': '96f804e1-f600-4faa-95a6-ce597e7db120',
       'length': '175000',
       'title': 'U‐Fig'},
      'title': 'U-Fig',
      'track_or_recording_length': '175000'},
     {'id': 'cdcf8572-3060-31ca-a72c-1ded81ca1f7a',
      'length': '328000',
      'number': '8',
      'position': '8',
      'recording': {'id': '26ba38f0-b26b-48b7-8e77-226b22a55f79',
       'length': '328000',
       'title': 'Holy Mountains'},
      'track_or_recording_length': '328000'},
     {'id': 'f9f00cb0-5635-3217-a2a0-bd61917eb0df',
      'length': '171000',
      'number': '9',
      'position': '9',
      'recording': {'id': '039f3379-3a69-4e75-a882-df1c4e1608aa',
       'length': '171000',
       'title': 'Vicinity of Obscenity'},
      'track_or_recording_length': '171000'},
     {'id': 'cdd45914-6741-353e-bbb5-d281048ff24f',
      'length': '164000',
      'number': '10',
      'position': '10',
      'recording': {'id': 'c24d541a-a9a8-4a22-84c6-5e6419459cf8',
       'length': '164000',
       'title': 'She’s Like Heroin'},
      'track_or_recording_length': '164000'},
     {'id': 'cfcf12ac-6831-3dd6-a2eb-9d0bfeee3f6d',
      'length': '167000',
      'number': '11',
      'position': '11',
      'recording': {'id': '0aff4799-849f-4f83-84f4-22cabbba2378',
       'length': '167000',
       'title': 'Lonely Day'},
      'track_or_recording_length': '167000'},
     {'id': '7e38bb38-ff62-3e41-a670-b7d77f578a1f',
      'length': '220000',
      'number': '12',
      'position': '12',
      'recording': {'id': 'e1b4d90f-2f44-4fe6-a826-362d4e3d9b88',
       'length': '220000',
       'title': 'Soldier Side'},
      'track_or_recording_length': '220000'}]}],
  'packaging': 'Digipak',
  'quality': 'normal',
  'release-event-count': 1,
  'release-event-list': [{'area': {'id': '489ce91b-6658-3307-9877-795b68554c98',
     'iso-3166-1-code-list': ['US'],
     'name': 'United States',
     'sort-name': 'United States'},
    'date': '2005'}],
  'status': 'Official',
  'text-representation': {'language': 'eng', 'script': 'Latn'},
  'title': 'Hypnotize'}}

_albums['get']['marsupial'] = {
    'release': {
        "artist-credit": [
            {
                "artist": {
                    "disambiguation": "George Shaw",
                    "id": "62c3befb-6366-4585-b256-809472333801",
                    "name": "Adhesive Wombat",
                    "sort-name": "Wombat, Adhesive"
                }
            }
        ],
        "artist-credit-phrase": "Adhesive Wombat",
        "country": "XW",
        "cover-art-archive": {
            "artwork": "true",
            "back": "false",
            "count": "1",
            "front": "true"
        },
        "date": "2013-06-05",
        "id": "a50d2a81-2a50-484d-9cb4-b9f6833f583e",
        "packaging": "None",
        "quality": "normal",
        "release-event-count": 1,
        "release-event-list": [
            {
                "area": {
                    "id": "525d4e18-3d00-31b9-a58b-a146a916de8f",
                    "iso-3166-1-code-list": [
                        "XW"
                    ],
                    "name": "[Worldwide]",
                    "sort-name": "[Worldwide]"
                },
                "date": "2013-06-05"
            }
        ],
        "status": "Official",
        "text-representation": {
            "language": "eng",
            "script": "Latn"
        },
        "title": "Marsupial Madness"
    }
}

_tracks = {'search': {}, 'get': {}}

_tracks['search']['8bitadventures'] = {
    'recording-list': [
        {
            "artist-credit": [
                {
                    "artist": {
                        "disambiguation": "George Shaw",
                        "id": "62c3befb-6366-4585-b256-809472333801",
                        "name": "Adhesive Wombat",
                        "sort-name": "Wombat, Adhesive"
                    }
                }
            ],
            "artist-credit-phrase": "Adhesive Wombat",
            "ext:score": "100",
            "id": "9968a9d6-8d92-4051-8f76-674e157b6eed",
            "length": "271000",
            "release-list": [
                {
                    "country": "XW",
                    "date": "2013-06-05",
                    "id": "a50d2a81-2a50-484d-9cb4-b9f6833f583e",
                    "medium-list": [
                        {
                            "format": "Digital Media",
                            "position": "1",
                            "track-count": 11,
                            "track-list": [
                                {
                                    "id": "64d43604-c1ee-4f45-a02c-030672d2fe27",
                                    "length": "271000",
                                    "number": "1",
                                    "title": "8-Bit Adventure",
                                    "track_or_recording_length": "271000"
                                }
                            ]
                        }
                    ],
                    "medium-track-count": 11,
                    "release-event-list": [
                        {
                            "area": {
                                "id": "525d4e18-3d00-31b9-a58b-a146a916de8f",
                                "iso-3166-1-code-list": [
                                    "XW"
                                ],
                                "name": "[Worldwide]",
                                "sort-name": "[Worldwide]"
                            },
                            "date": "2013-06-05"
                        }
                    ],
                    "release-group": {
                        "id": "447b4979-2178-405c-bfe6-46bf0b09e6c7",
                        "primary-type": "Album",
                        "type": "Album"
                    },
                    "status": "Official",
                    "title": "Marsupial Madness"
                }
            ],
            "title": "8-Bit Adventure",
            "tag-list": [
                {
                    "count": "2",
                    "name": "techno"
                },
                {
                    "count": "2",
                    "name": "good-music"
                },
            ],
        },
    ]
}

_tracks['get']['8bitadventures'] = {'recording': _tracks['search']['8bitadventures']['recording-list'][0]}
_tracks['get']['chop_suey'] = {
    'recording': {
        'id': '46c7368a-013a-47b6-97cc-e55e7ab25213',
        'length': '210240',
        'title': 'Chop Suey!',
        'work-relation-list': [{'target': 'e2ecabc4-1b9d-30b2-8f30-3596ec423dc5',
        'type': 'performance',
        'type-id': 'a3005666-a872-32c3-ad06-98af558e99b0',
        'work': {'id': 'e2ecabc4-1b9d-30b2-8f30-3596ec423dc5',
            'language': 'eng',
            'title': 'Chop Suey!'}}]}}

_works = {'search': {}, 'get': {}}
_works['get']['chop_suey'] = {'work': {'id': 'e2ecabc4-1b9d-30b2-8f30-3596ec423dc5',
  'language': 'eng',
  'recording-relation-list': [{'direction': 'backward',
    'recording': {'disambiguation': 'edit',
     'id': '07ca77cf-f513-4e9c-b190-d7e24bbad448',
     'length': '170893',
     'title': 'Chop Suey!'},
    'target': '07ca77cf-f513-4e9c-b190-d7e24bbad448',
    'type': 'performance',
    'type-id': 'a3005666-a872-32c3-ad06-98af558e99b0'},
  ],
  'title': 'Chop Suey!',
  'type': 'Song',
  'url-relation-list': [{'direction': 'backward',
    'target': 'http://lyrics.wikia.com/System_Of_A_Down:Chop_Suey!',
    'type': 'lyrics',
    'type-id': 'e38e65aa-75e0-42ba-ace0-072aeb91a538'}]}}


@pytest.fixture()
def artists():
    return _artists


@pytest.fixture()
def albums():
    return _albums


@pytest.fixture()
def tracks():
    return _tracks


@pytest.fixture()
def works():
    return _works


@pytest.fixture()
def lyricswiki_content():
    return """<!doctype html>
<html lang="en" dir="ltr">
<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
<meta name="generator" content="MediaWiki 1.19.24" />
<meta name="keywords" content="Chop Suey! lyrics,System Of A Down Chop Suey! lyrics,Chop Suey! by System Of A Down lyrics,lyrics,LyricWiki,LyricWikia,lyricwiki,System Of A Down:Chop Suey!,System Of A Down,System Of A Down:Toxicity (2001),Enter Shikari,Enter Shikari:Chop Suey!,&quot;Weird Al&quot; Yankovic,&quot;Weird Al&quot; Yankovic:Angry White Boy Polka,Renard,Renard:Physicality,System Of A Down:Chop Suey!/pt,Daron Malakian" />
<meta name="description" content="Chop Suey! This song is by System of a Down and appears on the album Toxicity (2001)." />
<meta name="twitter:card" content="summary" />
<meta name="twitter:site" content="@Wikia" />
<meta name="twitter:url" content="http://lyrics.wikia.com/wiki/System_Of_A_Down:Chop_Suey!" />
<meta name="twitter:title" content="System Of A Down:Chop Suey! Lyrics - LyricWikia - Wikia" />
<meta name="twitter:description" content="Chop Suey! This song is by System of a Down and appears on the album Toxicity (2001)." />
<link rel="canonical" href="http://lyrics.wikia.com/wiki/System_Of_A_Down:Chop_Suey!" />
<link rel="alternate" type="application/x-wiki" title="Edit" href="/wiki/System_Of_A_Down:Chop_Suey!?action=edit" />
<link rel="edit" title="Edit" href="/wiki/System_Of_A_Down:Chop_Suey!?action=edit" />
<link rel="apple-touch-icon" href="http://img4.wikia.nocookie.net/__cb22/lyricwiki/images/b/bc/Wiki.png" />
<link rel="shortcut icon" href="http://slot1.images.wikia.nocookie.net/__cb1474018633/common/skins/common/images/favicon.ico" />
<link rel="search" type="application/opensearchdescription+xml" href="/opensearch_desc.php" title="LyricWikia (en)" />
<link rel="EditURI" type="application/rsd+xml" href="http://lyrics.wikia.com/api.php?action=rsd" />
<link rel="copyright" href="/wiki/LyricWiki:Copyrights" />
<link rel="alternate" type="application/atom+xml" title="LyricWikia Atom feed" href="/wiki/Special:RecentChanges?feed=atom" />
<title>System Of A Down:Chop Suey! Lyrics - LyricWikia - Wikia</title>

<body>
<div class='lyricbox'>
<i>&#87;&#101;&#39;&#114;&#101;&#32;&#114;&#111;&#108;&#108;&#105;&#110;&#103;&#32;&#34;&#83;&#117;&#105;&#99;&#105;&#100;&#101;&#34;&#46;</i><br /><br />&#87;&#97;&#107;&#101;&#32;&#117;&#112;&#32;<i>&#40;&#119;&#97;&#107;&#101;&#32;&#117;&#112;&#41;</i><br />&#71;&#114;&#97;&#98;&#32;&#97;&#32;&#98;&#114;&#117;&#115;&#104;&#32;&#97;&#110;&#100;&#32;&#112;&#117;&#116;&#32;&#111;&#110;&#32;&#97;&#32;&#108;&#105;&#116;&#116;&#108;&#101;&#32;&#109;&#97;&#107;&#101;&#117;&#112;<br />&#72;&#105;&#100;&#101;&#32;&#116;&#104;&#101;&#32;&#115;&#99;&#97;&#114;&#115;&#32;&#116;&#111;&#32;&#102;&#97;&#100;&#101;&#32;&#97;&#119;&#97;&#121;&#32;&#116;&#104;&#101;&#32;&#115;&#104;&#97;&#107;&#101;&#117;&#112;&#32;<i>&#40;&#104;&#105;&#100;&#101;&#32;&#116;&#104;&#101;&#32;&#115;&#99;&#97;&#114;&#115;&#32;&#116;&#111;&#32;&#102;&#97;&#100;&#101;&#32;&#97;&#119;&#97;&#121;&#32;&#116;&#104;&#101;&#41;</i><br />&#87;&#104;&#121;&#39;&#100;&#32;&#121;&#111;&#117;&#32;&#108;&#101;&#97;&#118;&#101;&#32;&#116;&#104;&#101;&#32;&#107;&#101;&#121;&#115;&#32;&#117;&#112;&#111;&#110;&#32;&#116;&#104;&#101;&#32;&#116;&#97;&#98;&#108;&#101;&#63;<br />&#72;&#101;&#114;&#101;&#32;&#121;&#111;&#117;&#32;&#103;&#111;&#44;&#32;&#99;&#114;&#101;&#97;&#116;&#101;&#32;&#97;&#110;&#111;&#116;&#104;&#101;&#114;&#32;&#102;&#97;&#98;&#108;&#101;<br /><br />&#89;&#111;&#117;&#32;&#119;&#97;&#110;&#116;&#101;&#100;&#32;&#116;&#111;<br />&#71;&#114;&#97;&#98;&#32;&#97;&#32;&#98;&#114;&#117;&#115;&#104;&#32;&#97;&#110;&#100;&#32;&#112;&#117;&#116;&#32;&#97;&#32;&#108;&#105;&#116;&#116;&#108;&#101;&#32;&#109;&#97;&#107;&#101;&#117;&#112;<br />&#89;&#111;&#117;&#32;&#119;&#97;&#110;&#116;&#101;&#100;&#32;&#116;&#111;<br />&#72;&#105;&#100;&#101;&#32;&#116;&#104;&#101;&#32;&#115;&#99;&#97;&#114;&#115;&#32;&#116;&#111;&#32;&#102;&#97;&#100;&#101;&#32;&#97;&#119;&#97;&#121;&#32;&#116;&#104;&#101;&#32;&#115;&#104;&#97;&#107;&#101;&#117;&#112;<br />&#89;&#111;&#117;&#32;&#119;&#97;&#110;&#116;&#101;&#100;&#32;&#116;&#111;<br />&#87;&#104;&#121;&#39;&#100;&#32;&#121;&#111;&#117;&#32;&#108;&#101;&#97;&#118;&#101;&#32;&#116;&#104;&#101;&#32;&#107;&#101;&#121;&#115;&#32;&#117;&#112;&#111;&#110;&#32;&#116;&#104;&#101;&#32;&#116;&#97;&#98;&#108;&#101;&#63;<br />&#89;&#111;&#117;&#32;&#119;&#97;&#110;&#116;&#101;&#100;&#32;&#116;&#111;<br /><br />&#73;&#32;&#100;&#111;&#110;&#39;&#116;&#32;&#116;&#104;&#105;&#110;&#107;&#32;&#121;&#111;&#117;&#32;&#116;&#114;&#117;&#115;&#116;<br />&#73;&#110;&#32;&#109;&#121;&#32;&#115;&#101;&#108;&#102;&#45;&#114;&#105;&#103;&#104;&#116;&#101;&#111;&#117;&#115;&#32;&#115;&#117;&#105;&#99;&#105;&#100;&#101;<br />&#73;&#32;&#99;&#114;&#121;&#32;&#119;&#104;&#101;&#110;&#32;&#97;&#110;&#103;&#101;&#108;&#115;&#32;&#100;&#101;&#115;&#101;&#114;&#118;&#101;&#32;&#116;&#111;&#32;&#100;&#105;&#101;<br /><br />&#87;&#97;&#107;&#101;&#32;&#117;&#112;&#32;<i>&#40;&#119;&#97;&#107;&#101;&#32;&#117;&#112;&#41;</i><br />&#71;&#114;&#97;&#98;&#32;&#97;&#32;&#98;&#114;&#117;&#115;&#104;&#32;&#97;&#110;&#100;&#32;&#112;&#117;&#116;&#32;&#111;&#110;&#32;&#97;&#32;&#108;&#105;&#116;&#116;&#108;&#101;&#32;&#109;&#97;&#107;&#101;&#117;&#112;<br />&#72;&#105;&#100;&#101;&#32;&#116;&#104;&#101;&#32;&#115;&#99;&#97;&#114;&#115;&#32;&#116;&#111;&#32;&#102;&#97;&#100;&#101;&#32;&#97;&#119;&#97;&#121;&#32;&#116;&#104;&#101;&#32;<i>&#40;&#104;&#105;&#100;&#101;&#32;&#116;&#104;&#101;&#32;&#115;&#99;&#97;&#114;&#115;&#32;&#116;&#111;&#32;&#102;&#97;&#100;&#101;&#32;&#97;&#119;&#97;&#121;&#32;&#116;&#104;&#101;&#41;</i><br />&#87;&#104;&#121;&#39;&#100;&#32;&#121;&#111;&#117;&#32;&#108;&#101;&#97;&#118;&#101;&#32;&#116;&#104;&#101;&#32;&#107;&#101;&#121;&#115;&#32;&#117;&#112;&#111;&#110;&#32;&#116;&#104;&#101;&#32;&#116;&#97;&#98;&#108;&#101;&#63;<br />&#72;&#101;&#114;&#101;&#32;&#121;&#111;&#117;&#32;&#103;&#111;&#44;&#32;&#99;&#114;&#101;&#97;&#116;&#101;&#32;&#97;&#110;&#111;&#116;&#104;&#101;&#114;&#32;&#102;&#97;&#98;&#108;&#101;<br /><br />&#89;&#111;&#117;&#32;&#119;&#97;&#110;&#116;&#101;&#100;&#32;&#116;&#111;<br />&#71;&#114;&#97;&#98;&#32;&#97;&#32;&#98;&#114;&#117;&#115;&#104;&#32;&#97;&#110;&#100;&#32;&#112;&#117;&#116;&#32;&#97;&#32;&#108;&#105;&#116;&#116;&#108;&#101;&#32;&#109;&#97;&#107;&#101;&#117;&#112;<br />&#89;&#111;&#117;&#32;&#119;&#97;&#110;&#116;&#101;&#100;&#32;&#116;&#111;<br />&#72;&#105;&#100;&#101;&#32;&#116;&#104;&#101;&#32;&#115;&#99;&#97;&#114;&#115;&#32;&#116;&#111;&#32;&#102;&#97;&#100;&#101;&#32;&#97;&#119;&#97;&#121;&#32;&#116;&#104;&#101;&#32;&#115;&#104;&#97;&#107;&#101;&#117;&#112;<br />&#89;&#111;&#117;&#32;&#119;&#97;&#110;&#116;&#101;&#100;&#32;&#116;&#111;<br />&#87;&#104;&#121;&#39;&#100;&#32;&#121;&#111;&#117;&#32;&#108;&#101;&#97;&#118;&#101;&#32;&#116;&#104;&#101;&#32;&#107;&#101;&#121;&#115;&#32;&#117;&#112;&#111;&#110;&#32;&#116;&#104;&#101;&#32;&#116;&#97;&#98;&#108;&#101;&#63;<br />&#89;&#111;&#117;&#32;&#119;&#97;&#110;&#116;&#101;&#100;&#32;&#116;&#111;<br /><br />&#73;&#32;&#100;&#111;&#110;&#39;&#116;&#32;&#116;&#104;&#105;&#110;&#107;&#32;&#121;&#111;&#117;&#32;&#116;&#114;&#117;&#115;&#116;<br />&#73;&#110;&#32;&#109;&#121;&#32;&#115;&#101;&#108;&#102;&#45;&#114;&#105;&#103;&#104;&#116;&#101;&#111;&#117;&#115;&#32;&#115;&#117;&#105;&#99;&#105;&#100;&#101;<br />&#73;&#32;&#99;&#114;&#121;&#32;&#119;&#104;&#101;&#110;&#32;&#97;&#110;&#103;&#101;&#108;&#115;&#32;&#100;&#101;&#115;&#101;&#114;&#118;&#101;&#32;&#116;&#111;&#32;&#100;&#105;&#101;<br />&#73;&#110;&#32;&#109;&#121;&#32;&#115;&#101;&#108;&#102;&#45;&#114;&#105;&#103;&#104;&#116;&#101;&#111;&#117;&#115;&#32;&#115;&#117;&#105;&#99;&#105;&#100;&#101;<br />&#73;&#32;&#99;&#114;&#121;&#32;&#119;&#104;&#101;&#110;&#32;&#97;&#110;&#103;&#101;&#108;&#115;&#32;&#100;&#101;&#115;&#101;&#114;&#118;&#101;&#32;&#116;&#111;&#32;&#100;&#105;&#101;<br /><br />&#70;&#97;&#116;&#104;&#101;&#114;&#32;<i>&#40;&#102;&#97;&#116;&#104;&#101;&#114;&#41;</i><br />&#70;&#97;&#116;&#104;&#101;&#114;&#32;<i>&#40;&#102;&#97;&#116;&#104;&#101;&#114;&#41;</i><br />&#70;&#97;&#116;&#104;&#101;&#114;&#32;<i>&#40;&#102;&#97;&#116;&#104;&#101;&#114;&#41;</i><br />&#70;&#97;&#116;&#104;&#101;&#114;&#32;<i>&#40;&#102;&#97;&#116;&#104;&#101;&#114;&#41;</i><br />&#70;&#97;&#116;&#104;&#101;&#114;&#44;&#32;&#105;&#110;&#116;&#111;&#32;&#121;&#111;&#117;&#114;&#32;&#104;&#97;&#110;&#100;&#115;&#32;&#73;&#32;&#99;&#111;&#109;&#109;&#105;&#116;&#32;&#109;&#121;&#32;&#115;&#112;&#105;&#114;&#105;&#116;<br />&#70;&#97;&#116;&#104;&#101;&#114;&#44;&#32;&#105;&#110;&#116;&#111;&#32;&#121;&#111;&#117;&#114;&#32;&#104;&#97;&#110;&#100;&#115;<br /><br />&#87;&#104;&#121;&#32;&#104;&#97;&#118;&#101;&#32;&#121;&#111;&#117;&#32;&#102;&#111;&#114;&#115;&#97;&#107;&#101;&#110;&#32;&#109;&#101;&#63;<br />&#73;&#110;&#32;&#121;&#111;&#117;&#114;&#32;&#101;&#121;&#101;&#115;&#32;&#102;&#111;&#114;&#115;&#97;&#107;&#101;&#110;&#32;&#109;&#101;<br />&#73;&#110;&#32;&#121;&#111;&#117;&#114;&#32;&#116;&#104;&#111;&#117;&#103;&#104;&#116;&#115;&#32;&#102;&#111;&#114;&#115;&#97;&#107;&#101;&#110;&#32;&#109;&#101;<br />&#73;&#110;&#32;&#121;&#111;&#117;&#114;&#32;&#104;&#101;&#97;&#114;&#116;&#32;&#102;&#111;&#114;&#115;&#97;&#107;&#101;&#110;&#32;&#109;&#101;&#44;&#32;&#111;&#104;<br /><br />&#84;&#114;&#117;&#115;&#116;&#32;&#105;&#110;&#32;&#109;&#121;&#32;&#115;&#101;&#108;&#102;&#45;&#114;&#105;&#103;&#104;&#116;&#101;&#111;&#117;&#115;&#32;&#115;&#117;&#105;&#99;&#105;&#100;&#101;<br />&#73;&#32;&#99;&#114;&#121;&#32;&#119;&#104;&#101;&#110;&#32;&#97;&#110;&#103;&#101;&#108;&#115;&#32;&#100;&#101;&#115;&#101;&#114;&#118;&#101;&#32;&#116;&#111;&#32;&#100;&#105;&#101;<br />&#73;&#110;&#32;&#109;&#121;&#32;&#115;&#101;&#108;&#102;&#45;&#114;&#105;&#103;&#104;&#116;&#101;&#111;&#117;&#115;&#32;&#115;&#117;&#105;&#99;&#105;&#100;&#101;<br />&#73;&#32;&#99;&#114;&#121;&#32;&#119;&#104;&#101;&#110;&#32;&#97;&#110;&#103;&#101;&#108;&#115;&#32;&#100;&#101;&#115;&#101;&#114;&#118;&#101;&#32;&#116;&#111;&#32;&#100;&#105;&#101;&#10;
</div>
</body>
</html>"""


@pytest.fixture()
def binary_cover():
    return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x02\x01\x00H\x00H\x00\x00\xff\xed\x08\xaePhotoshop 3.0\x008BIM\x03\xe9\x00\x00\x00\x00\x00x\x00\x03\x00\x00\x00H\x00H\x00\x00\x00\x00\x02\xd8\x02(\xff\xe1\xff\xe2\x02\xf9\x02F\x03G\x05(\x03\xfc\x00\x02\x00\x00\x00H\x00H\x00\x00\x00\x00\x02\xd8\x02(\x00\x01\x00\x00\x00d\x00\x00\x00\x01\x00\x03\x03\x03\x00\x00\x00\x01\'\x0f\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00`\x08\x00\x19\x01\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x008BIM\x03\xed\x00\x00\x00\x00\x00\x10\x00H\x00\x00\x00\x01\x00\x01\x00H\x00\x00\x00\x01\x00\x018BIM\x03\xf3\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x008BIM\x04\n\x00\x00\x00\x00\x00\x01\x00\x008BIM\'\x10\x00\x00\x00\x00\x00\n\x00\x01\x00\x00\x00\x00\x00\x00\x00\x028BIM\x03\xf5\x00\x00\x00\x00\x00H\x00/ff\x00\x01\x00lff\x00\x06\x00\x00\x00\x00\x00\x01\x00/ff\x00\x01\x00\xa1\x99\x9a\x00\x06\x00\x00\x00\x00\x00\x01\x002\x00\x00\x00\x01\x00Z\x00\x00\x00\x06\x00\x00\x00\x00\x00\x01\x005\x00\x00\x00\x01\x00-\x00\x00\x00\x06\x00\x00\x00\x00\x00\x018BIM\x03\xf8\x00\x00\x00\x00\x00p\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x03\xe8\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x03\xe8\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x03\xe8\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x03\xe8\x00\x008BIM\x04\x00\x00\x00\x00\x00\x00\x02\x00\x018BIM\x04\x02\x00\x00\x00\x00\x00\x04\x00\x00\x00\x008BIM\x04\x08\x00\x00\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x02@\x00\x00\x02@\x00\x00\x00\x008BIM\x04\t\x00\x00\x00\x00\x06\x9b\x00\x00\x00\x01\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x01\x80\x00\x00\xc0\x00\x00\x00\x06\x7f\x00\x18\x00\x01\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x02\x01\x00H\x00H\x00\x00\xff\xfe\x00\'File written by Adobe Photoshop\xa8 4.0\x00\xff\xee\x00\x0eAdobe\x00d\x80\x00\x00\x00\x01\xff\xdb\x00\x84\x00\x0c\x08\x08\x08\t\x08\x0c\t\t\x0c\x11\x0b\n\x0b\x11\x15\x0f\x0c\x0c\x0f\x15\x18\x13\x13\x15\x13\x13\x18\x11\x0c\x0c\x0c\x0c\x0c\x0c\x11\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x01\r\x0b\x0b\r\x0e\r\x10\x0e\x0e\x10\x14\x0e\x0e\x0e\x14\x14\x0e\x0e\x0e\x0e\x14\x11\x0c\x0c\x0c\x0c\x0c\x11\x11\x0c\x0c\x0c\x0c\x0c\x0c\x11\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\xff\xc0\x00\x11\x08\x00\x80\x00\x80\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xdd\x00\x04\x00\x08\xff\xc4\x01?\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x03\x00\x01\x02\x04\x05\x06\x07\x08\t\n\x0b\x01\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x10\x00\x01\x04\x01\x03\x02\x04\x02\x05\x07\x06\x08\x05\x03\x0c3\x01\x00\x02\x11\x03\x04!\x121\x05AQa\x13"q\x812\x06\x14\x91\xa1\xb1B#$\x15R\xc1b34r\x82\xd1C\x07%\x92S\xf0\xe1\xf1cs5\x16\xa2\xb2\x83&D\x93TdE\xc2\xa3t6\x17\xd2U\xe2e\xf2\xb3\x84\xc3\xd3u\xe3\xf3F\'\x94\xa4\x85\xb4\x95\xc4\xd4\xe4\xf4\xa5\xb5\xc5\xd5\xe5\xf5Vfv\x86\x96\xa6\xb6\xc6\xd6\xe6\xf67GWgw\x87\x97\xa7\xb7\xc7\xd7\xe7\xf7\x11\x00\x02\x02\x01\x02\x04\x04\x03\x04\x05\x06\x07\x07\x06\x055\x01\x00\x02\x11\x03!1\x12\x04AQaq"\x13\x052\x81\x91\x14\xa1\xb1B#\xc1R\xd1\xf03$b\xe1r\x82\x92CS\x15cs4\xf1%\x06\x16\xa2\xb2\x83\x07&5\xc2\xd2D\x93T\xa3\x17dEU6te\xe2\xf2\xb3\x84\xc3\xd3u\xe3\xf3F\x94\xa4\x85\xb4\x95\xc4\xd4\xe4\xf4\xa5\xb5\xc5\xd5\xe5\xf5Vfv\x86\x96\xa6\xb6\xc6\xd6\xe6\xf6\'7GWgw\x87\x97\xa7\xb7\xc7\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xf5T\x92I%)$\x92IJI$\x92R\x92I$\x94\xa4\x92I%)$\x92IJI$\x92R\x92I$\x94\xff\x00\xff\xd0\xf5T\x92I%)$\x92IJI%\xe7\xff\x00Z\x7f\xc6\xbf\xfc\xde\xeb\xb9]\x1f\xf6_\xda~\xcd\xe9\xfe\x9b\xed\x1e\x9e\xefR\xba\xef\xfeo\xec\xf6\xed\xdb\xea\xec\xfeq%>\x80\x92\xf2\xaf\xfc}?\xf3I\xff\x00\xb3_\xfb\xe8\x97\xfe>\x9f\xf9\xa4\xff\x00\xd9\xaf\xfd\xf4IO\xaa\xa4\xbc\xab\xff\x00\x1fO\xfc\xd2\x7f\xec\xd7\xfe\xfa%\xff\x00\x8f\xa7\xfei?\xf6k\xff\x00}\x12S\xea\xa9.+\xeaW\xf8\xc8\xff\x00\x9d}V\xde\x9d\xfb;\xec~\x96;\xb2=O[\xd5\x9d\xaf\xaa\xad\x9b=\n\x7f\xd3}-\xeb\xb5IJI$\x92R\x92I$\x94\xff\x00\xff\xd1\xf5T\x92I%)$\x97\x9f\xff\x00\x8d\x7f\xad=w\xea\xf7\xec\xbf\xd8\xf9_f\xfbO\xda=o\xd1\xd7f\xefO\xec\xfe\x9f\xf3\xf5\xdb\xb7o\xabg\xd0IO\xa0/\x9f\xff\x00\xc6\x97\xfe.\xfa\x9f\xfdc\xff\x00m\xf1\xd2\xff\x00\xc7K\xeb\xdf\xfeY\xff\x00\xe0\x18\xff\x00\xfb\xce\xb9\xfe\xa9\xd53\xfa\xbe}\xbdG\xa8\xdb\xeb\xe5\xdf\xb7\xd4\xb3kY;\x1a\xda\x99\xec\xa9\xac\xaf\xf9\xb63\xf3\x12SU$\x92IJI$\x92S\xdf\xff\x00\x89O\xfcUe\x7f\xe1\x0b?\xf3\xf6*\xf6\xb5\xf3/D\xeb\xfd[\xa0\xe5?3\xa4\xdf\xf6l\x8b+59\xfb\x18\xf9a-\xb1\xcd\xdb{-g\xd3\xa9\x8bk\xff\x00\x1d/\xaf\x7f\xf9g\xff\x00\x80c\xff\x00\xef:J~\x80Iq\xff\x00\xe2\xbf\xaf\xf5n\xbd\xd023:\xb5\xff\x00i\xc8\xaf-\xf55\xfb\x18\xc8`\xae\x8b\x1a\xdd\xb42\xa6};^\xbb\x04\x94\xa4\x92I%?\xff\xd2\xf5T\x92I%)yW\xf8\xf4\xff\x00\xbcO\xfd\n\xff\x00\xddE\xea\xab\xca\xbf\xc7\xa7\xfd\xe2\x7f\xe8W\xfe\xea$\xa7\xca\x92I$\x94\xa4\x92I%)$\x92IJI$\x92S\xed_\xe2S\xff\x00\x12\xb9_\xf8~\xcf\xfc\xf3\x8a\xbd\x01y\xff\x00\xf8\x94\xff\x00\xc4\xaeW\xfe\x1f\xb3\xff\x00<\xe2\xaf@IJI$\x92S\xff\xd3\xf5T\x92I%)yW\xf8\xf4\xff\x00\xbcO\xfd\n\xff\x00\xddE\xea\xab\xca\xbf\xc7\xa7\xfd\xe2\x7f\xe8W\xfe\xea$\xa7\xca\x92I$\x94\xa4\x92I%)$\x92IJI$\x92S\xed_\xe2S\xff\x00\x12\xb9_\xf8~\xcf\xfc\xf3\x8a\xbd\x01y\xff\x00\xf8\x94\xff\x00\xc4\xaeW\xfe\x1f\xb3\xff\x00<\xe2\xaf@IJI$\x92S\xff\xd4\xf5T\x92I%)q_\xe3#\xeaWU\xfa\xd7\xfb;\xf6u\xb8\xf5}\x8f\xd6\xf5>\xd0\xe7\xb6}_Cf\xcfJ\xab\xbf\xd0\xbfr\xedRIO\x8a\x7f\xe3)\xf5\xab\xfe\xe5`\x7f\xdb\x97\x7f\xef*\xe4:\xff\x00D\xca\xe8=Z\xfe\x93\x98\xfa\xec\xc8\xc6\xd9\xbd\xd5\x12Xw\xb1\x97\xb7k\xacmO\xfa\x16\xfe\xe2\xfai|\xff\x00\xfe4\xbf\xf1w\xd4\xff\x00\xeb\x1f\xfbo\x8e\x92\x9eU$\x92IJI$\x92S\xb1\xf5_\xea\xbfP\xfa\xd1\xd4,\xc0\xc0\xb2\x9a\xad\xaa\x93{\x9dys[\xb5\xae\xae\xa2\x01\xaa\xbb\x9d\xbfu\xcd\xfc\xd5\xd3\xff\x00\xe3)\xf5\xab\xfe\xe5`\x7f\xdb\x97\x7f\xef*_\xe2S\xff\x00\x15Y_\xf8B\xcf\xfc\xfd\x8a\xbd\xad%<\xbf\xf8\xbc\xfa\xaf\xd4>\xab\xf4[\xb03\xec\xa6\xdbm\xc9u\xedu\x05\xcen\xd7WM@\x13mt\xbb~\xea]\xf9\xab\xa8I$\x94\xa4\x92I%?\xff\xd5\xf5T\x92I%)$\x92IJ\\\x7f_\xff\x00\x15\xfd\x03\xafuk\xfa\xb6fF]y\x19;7\xb6\xa7\xd6\x1861\x947kl\xa2\xd7\xfd\n\xbf}v\t$\xa7\xcf\xff\x00\xf1\x94\xfa\xab\xff\x00r\xb3\xff\x00\xed\xca\x7f\xf7\x95/\xfce>\xaa\xff\x00\xdc\xac\xff\x00\xfbr\x9f\xfd\xe5^\x80\x92J|\xff\x00\xff\x00\x19O\xaa\xbf\xf7+?\xfe\xdc\xa7\xff\x00yR\xff\x00\xc6S\xea\xaf\xfd\xca\xcf\xff\x00\xb7)\xff\x00\xdeU\xe8\t$\xa7\x97\xfa\xaf\xfe/:/\xd5~\xa1f~\x05\xd96\xdbm&\x876\xf7V\xe6\xeds\xab\xb4\x90*\xa6\x97o\xddK\x7f9u\t$\x92\x94\x92I$\xa5$\x92I)\xff\xd6\xf5T\x92I%)$\x92IJI$\x92R\x92I$\x94\xa4\x92I%)$\x92IJI$\x92R\x92I$\x94\xff\x00\xff\xd9\x008BIM\x04\x06\x00\x00\x00\x00\x00\x07\x00\x03\x00\x00\x00\x01\x01\x00\xff\xfe\x00\'File written by Adobe Photoshop\xa8 4.0\x00\xff\xee\x00\x0eAdobe\x00d\x00\x00\x00\x00\x01\xff\xdb\x00\x84\x00\n\x07\x07\x07\x08\x07\n\x08\x08\n\x0f\n\x08\n\x0f\x12\r\n\n\r\x12\x14\x10\x10\x12\x10\x10\x14\x11\x0c\x0c\x0c\x0c\x0c\x0c\x11\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x01\x0b\x0c\x0c\x15\x13\x15"\x18\x18"\x14\x0e\x0e\x0e\x14\x14\x0e\x0e\x0e\x0e\x14\x11\x0c\x0c\x0c\x0c\x0c\x11\x11\x0c\x0c\x0c\x0c\x0c\x0c\x11\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\xff\xc0\x00\x11\x08\x00\t\x00\t\x03\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xdd\x00\x04\x00\x02\xff\xc4\x01\xa2\x00\x00\x00\x07\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x04\x05\x03\x02\x06\x01\x00\x07\x08\t\n\x0b\x01\x00\x02\x02\x03\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x10\x00\x02\x01\x03\x03\x02\x04\x02\x06\x07\x03\x04\x02\x06\x02s\x01\x02\x03\x11\x04\x00\x05!\x121AQ\x06\x13a"q\x81\x142\x91\xa1\x07\x15\xb1B#\xc1R\xd1\xe13\x16b\xf0$r\x82\xf1%C4S\x92\xa2\xb2cs\xc25D\'\x93\xa3\xb36\x17Tdt\xc3\xd2\xe2\x08&\x83\t\n\x18\x19\x84\x94EF\xa4\xb4V\xd3U(\x1a\xf2\xe3\xf3\xc4\xd4\xe4\xf4eu\x85\x95\xa5\xb5\xc5\xd5\xe5\xf5fv\x86\x96\xa6\xb6\xc6\xd6\xe6\xf67GWgw\x87\x97\xa7\xb7\xc7\xd7\xe7\xf78HXhx\x88\x98\xa8\xb8\xc8\xd8\xe8\xf8)9IYiy\x89\x99\xa9\xb9\xc9\xd9\xe9\xf9*:JZjz\x8a\x9a\xaa\xba\xca\xda\xea\xfa\x11\x00\x02\x02\x01\x02\x03\x05\x05\x04\x05\x06\x04\x08\x03\x03m\x01\x00\x02\x11\x03\x04!\x121A\x05Q\x13a"\x06q\x81\x912\xa1\xb1\xf0\x14\xc1\xd1\xe1#B\x15Rbr\xf13$4C\x82\x16\x92S%\xa2c\xb2\xc2\x07s\xd25\xe2D\x83\x17T\x93\x08\t\n\x18\x19&6E\x1a\'dtU7\xf2\xa3\xb3\xc3()\xd3\xe3\xf3\x84\x94\xa4\xb4\xc4\xd4\xe4\xf4eu\x85\x95\xa5\xb5\xc5\xd5\xe5\xf5FVfv\x86\x96\xa6\xb6\xc6\xd6\xe6\xf6GWgw\x87\x97\xa7\xb7\xc7\xd7\xe7\xf78HXhx\x88\x98\xa8\xb8\xc8\xd8\xe8\xf89IYiy\x89\x99\xa9\xb9\xc9\xd9\xe9\xf9*:JZjz\x8a\x9a\xaa\xba\xca\xda\xea\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\x91\xea\xfa\xbf\xe6D_\x99\x16\x96\x16\x16\x8c\xdeWf\x84;\x88U\xa1hY\x7f\xd3\'\x9e\xf3\xedCq\x0bz\xfe\x94^\xbc?\xdc\xdb\xff\x00\xa3\xcd\xeb\x7f\xa4\xaa\xf4<U\xff\xd0\xec\xd8\xab\xb1W\xff\xd9'
