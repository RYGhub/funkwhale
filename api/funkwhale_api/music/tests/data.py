artists = {'search': {}, 'get': {}}
artists['search']['adhesive_wombat'] = {
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
artists['get']['adhesive_wombat'] = {'artist': artists['search']['adhesive_wombat']['artist-list'][0]}

artists['get']['soad'] = {
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

albums = {'search': {}, 'get': {}, 'get_with_includes': {}}
albums['search']['hypnotize'] = {
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
albums['get']['hypnotize'] = {'release': albums['search']['hypnotize']['release-list'][0]}
albums['get_with_includes']['hypnotize'] = {
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

albums['get']['marsupial'] = {
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

tracks = {'search': {}, 'get': {}}

tracks['search']['8bitadventures'] = {
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

tracks['get']['8bitadventures'] = {'recording': tracks['search']['8bitadventures']['recording-list'][0]}
tracks['get']['chop_suey'] = {
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

works = {'search': {}, 'get': {}}
works['get']['chop_suey'] = {'work': {'id': 'e2ecabc4-1b9d-30b2-8f30-3596ec423dc5',
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
