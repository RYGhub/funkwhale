import pytest

_artists = {'search': {}, 'get': {}}
_artists['search']['lost fingers'] = {
    'artist-count': 696,
    'artist-list': [
        {
            'country': 'CA',
            'sort-name': 'Lost Fingers, The',
            'id': 'ac16bbc0-aded-4477-a3c3-1d81693d58c9',
            'type': 'Group',
            'life-span': {
                'ended': 'false',
                'begin': '2008'
            },
            'area': {
                'sort-name': 'Canada',
                'id': '71bbafaa-e825-3e15-8ca9-017dcad1748b',
                'name': 'Canada'
            },
            'ext:score': '100',
            'name': 'The Lost Fingers'
        },
    ]
}
_artists['get']['lost fingers'] = {
    "artist": {
        "life-span": {
            "begin": "2008"
        },
        "type": "Group",
        "id": "ac16bbc0-aded-4477-a3c3-1d81693d58c9",
        "release-group-count": 8,
        "name": "The Lost Fingers",
        "release-group-list": [
            {
                "title": "Gypsy Kameleon",
                "first-release-date": "2010",
                "type": "Album",
                "id": "03d3f1d4-e2b0-40d3-8314-05f1896e93a0",
                "primary-type": "Album"
            },
            {
                "title": "Gitan Kameleon",
                "first-release-date": "2011-11-11",
                "type": "Album",
                "id": "243c0cd2-2492-4f5d-bf37-c7c76bed05b7",
                "primary-type": "Album"
            },
            {
                "title": "Pump Up the Jam \u2013 Do Not Cover, Pt. 3",
                "first-release-date": "2014-03-17",
                "type": "Single",
                "id": "4429befd-ff45-48eb-a8f4-cdf7bf007f3f",
                "primary-type": "Single"
            },
            {
                "title": "La Marquise",
                "first-release-date": "2012-03-27",
                "type": "Album",
                "id": "4dab4b96-0a6b-4507-a31e-2189e3e7bad1",
                "primary-type": "Album"
            },
            {
                "title": "Christmas Caravan",
                "first-release-date": "2016-11-11",
                "type": "Album",
                "id": "ca0a506d-6ba9-47c3-a712-de5ce9ae6b1f",
                "primary-type": "Album"
            },
            {
                "title": "Rendez-vous rose",
                "first-release-date": "2009-06-16",
                "type": "Album",
                "id": "d002f1a8-5890-4188-be58-1caadbbd767f",
                "primary-type": "Album"
            },
            {
                "title": "Wonders of the World",
                "first-release-date": "2014-05-06",
                "type": "Album",
                "id": "eeb644c2-5000-42fb-b959-e5e9cc2901c5",
                "primary-type": "Album"
            },
            {
                "title": "Lost in the 80s",
                "first-release-date": "2008-05-06",
                "type": "Album",
                "id": "f04ed607-11b7-3843-957e-503ecdd485d1",
                "primary-type": "Album"
            }
        ],
        "area": {
            "iso-3166-1-code-list": [
                "CA"
            ],
            "name": "Canada",
            "id": "71bbafaa-e825-3e15-8ca9-017dcad1748b",
            "sort-name": "Canada"
        },
        "sort-name": "Lost Fingers, The",
        "country": "CA"
    }
}


_release_groups = {'browse': {}}
_release_groups['browse']["lost fingers"] = {
    "release-group-list": [
        {
            "first-release-date": "2010",
            "type": "Album",
            "primary-type": "Album",
            "title": "Gypsy Kameleon",
            "id": "03d3f1d4-e2b0-40d3-8314-05f1896e93a0"
        },
        {
            "first-release-date": "2011-11-11",
            "type": "Album",
            "primary-type": "Album",
            "title": "Gitan Kameleon",
            "id": "243c0cd2-2492-4f5d-bf37-c7c76bed05b7"
        },
        {
            "first-release-date": "2014-03-17",
            "type": "Single",
            "primary-type": "Single",
            "title": "Pump Up the Jam \u2013 Do Not Cover, Pt. 3",
            "id": "4429befd-ff45-48eb-a8f4-cdf7bf007f3f"
        },
        {
            "first-release-date": "2012-03-27",
            "type": "Album",
            "primary-type": "Album",
            "title": "La Marquise",
            "id": "4dab4b96-0a6b-4507-a31e-2189e3e7bad1"
        },
        {
            "first-release-date": "2016-11-11",
            "type": "Album",
            "primary-type": "Album",
            "title": "Christmas Caravan",
            "id": "ca0a506d-6ba9-47c3-a712-de5ce9ae6b1f"
        },
        {
            "first-release-date": "2009-06-16",
            "type": "Album",
            "primary-type": "Album",
            "title": "Rendez-vous rose",
            "id": "d002f1a8-5890-4188-be58-1caadbbd767f"
        },
        {
            "first-release-date": "2014-05-06",
            "type": "Album",
            "primary-type": "Album",
            "title": "Wonders of the World",
            "id": "eeb644c2-5000-42fb-b959-e5e9cc2901c5"
        },
        {
            "first-release-date": "2008-05-06",
            "type": "Album",
            "primary-type": "Album",
            "title": "Lost in the 80s",
            "id": "f04ed607-11b7-3843-957e-503ecdd485d1"
        }
    ],
    "release-group-count": 8
}

_recordings = {'search': {}, 'get': {}}
_recordings['search']['brontide matador'] = {
    "recording-count": 1044,
    "recording-list": [
        {
            "ext:score": "100",
            "length": "366280",
            "release-list": [
                {
                    "date": "2011-05-30",
                    "medium-track-count": 8,
                    "release-event-list": [
                        {
                            "area": {
                                "name": "United Kingdom",
                                "sort-name": "United Kingdom",
                                "id": "8a754a16-0027-3a29-b6d7-2b40ea0481ed",
                                "iso-3166-1-code-list": ["GB"]
                            },
                            "date": "2011-05-30"
                        }
                    ],
                    "country": "GB",
                    "title": "Sans Souci",
                    "status": "Official",
                    "id": "fde538c8-ffef-47c6-9b5a-bd28f4070e5c",
                    "release-group": {
                        "type": "Album",
                        "id": "113ab958-cfb8-4782-99af-639d4d9eae8d",
                        "primary-type": "Album"
                    },
                    "medium-list": [
                        {
                            "format": "CD",
                            "track-list": [
                                {
                                    "track_or_recording_length": "366280",
                                    "id": "fe506782-a5cb-3d89-9b3e-86287be05768",
                                    "length": "366280",
                                    "title": "Matador", "number": "1"
                                }
                            ],
                            "position": "1",
                            "track-count": 8
                        }
                    ]
                },
            ]
        }
    ]
}

_releases = {'search': {}, 'get': {}, 'browse': {}}
_releases['search']['brontide matador'] = {
    "release-count": 116, "release-list": [
        {
            "ext:score": "100",
            "date": "2009-04-02",
            "release-event-list": [
                {
                    "area": {
                        "name": "[Worldwide]",
                        "sort-name": "[Worldwide]",
                        "id": "525d4e18-3d00-31b9-a58b-a146a916de8f",
                        "iso-3166-1-code-list": ["XW"]
                    },
                    "date": "2009-04-02"
                }
            ],
            "label-info-list": [
                {
                    "label": {
                        "name": "Holy Roar",
                        "id": "6e940f35-961d-4ac3-bc2a-569fc211c2e3"
                    }
                }
            ],
            "medium-track-count": 3,
            "packaging": "None",
            "artist-credit": [
                {
                    "artist": {
                        "name": "Brontide",
                        "sort-name": "Brontide",
                        "id": "2179fbd2-3c88-4b94-a778-eb3daf1e81a1"
                    }
                }
            ],
            "artist-credit-phrase": "Brontide",
            "country": "XW",
            "title": "Brontide EP",
            "status": "Official",
            "barcode": "",
            "id": "59fbd4d1-6121-40e3-9b76-079694fe9702",
            "release-group": {
                "type": "EP",
                "secondary-type-list": ["Demo"],
                "id": "b9207129-2d03-4a68-8a53-3c46fe7d2810",
                "primary-type": "EP"
            },
            "medium-list": [
                {
                    "disc-list": [],
                    "format": "Digital Media",
                    "disc-count": 0,
                    "track-count": 3,
                    "track-list": []
                }
            ],
            "medium-count": 1,
            "text-representation": {
                "script": "Latn",
                "language": "eng"
            }
        },
    ]
}

_releases['browse']['Lost in the 80s'] = {
    "release-count": 3,
    "release-list": [
        {
            "quality": "normal",
            "status": "Official",
            "text-representation": {
                "script": "Latn",
                "language": "eng"
            },
            "title": "Lost in the 80s",
            "date": "2008-05-06",
            "release-event-count": 1,
            "id": "34e27fa0-aad4-4cc5-83a3-0f97089154dc",
            "barcode": "622406580223",
            "medium-count": 1,
            "release-event-list": [
                {
                    "area": {
                        "iso-3166-1-code-list": [
                            "CA"
                        ],
                        "id": "71bbafaa-e825-3e15-8ca9-017dcad1748b",
                        "name": "Canada",
                        "sort-name": "Canada"
                    },
                    "date": "2008-05-06"
                }
            ],
            "country": "CA",
            "cover-art-archive": {
                "back": "false",
                "artwork": "false",
                "front": "false",
                "count": "0"
            },
            "medium-list": [
                {
                    "position": "1",
                    "track-count": 12,
                    "format": "CD",
                    "track-list": [
                        {
                            "id": "1662bdf8-31d6-3f6e-846b-fe88c087b109",
                            "length": "228000",
                            "recording": {
                                "id": "2e0dbf37-65af-4408-8def-7b0b3cb8426b",
                                "length": "228000",
                                "title": "Pump Up the Jam"
                            },
                            "track_or_recording_length": "228000",
                            "position": "1",
                            "number": "1"
                        },
                        {
                            "id": "01a8cf99-2170-3d3f-96ef-5e4ef7a015a4",
                            "length": "231000",
                            "recording": {
                                "id": "57017e2e-625d-4e7b-a445-47cdb0224dd2",
                                "length": "231000",
                                "title": "You Give Love a Bad Name"
                            },
                            "track_or_recording_length": "231000",
                            "position": "2",
                            "number": "2"
                        },
                        {
                            "id": "375a7ce7-5a41-3fbf-9809-96d491401034",
                            "length": "189000",
                            "recording": {
                                "id": "a948672b-b42d-44a5-89b0-7e9ab6a7e11d",
                                "length": "189000",
                                "title": "You Shook Me All Night Long"
                            },
                            "track_or_recording_length": "189000",
                            "position": "3",
                            "number": "3"
                        },
                        {
                            "id": "ed7d823e-76da-31be-82a8-770288e27d32",
                            "length": "253000",
                            "recording": {
                                "id": "6e097e31-f37b-4fae-8ad0-ada57f3091a7",
                                "length": "253000",
                                "title": "Incognito"
                            },
                            "track_or_recording_length": "253000",
                            "position": "4",
                            "number": "4"
                        },
                        {
                            "id": "76ac8c77-6a99-34d9-ae4d-be8f056d50e0",
                            "length": "221000",
                            "recording": {
                                "id": "faa922e6-e834-44ee-8125-79e640a690e3",
                                "length": "221000",
                                "title": "Touch Me"
                            },
                            "track_or_recording_length": "221000",
                            "position": "5",
                            "number": "5"
                        },
                        {
                            "id": "d0a87409-2be6-3ab7-8526-4313e7134be1",
                            "length": "228000",
                            "recording": {
                                "id": "02da8148-60d8-4c79-ab31-8d90d233d711",
                                "length": "228000",
                                "title": "Part-Time Lover"
                            },
                            "track_or_recording_length": "228000",
                            "position": "6",
                            "number": "6"
                        },
                        {
                            "id": "02c5384b-5ca9-38e9-8b7c-c08dce608deb",
                            "length": "248000",
                            "recording": {
                                "id": "40085704-d6ab-44f6-a4d8-b27c9ca25b31",
                                "length": "248000",
                                "title": "Fresh"
                            },
                            "track_or_recording_length": "248000",
                            "position": "7",
                            "number": "7"
                        },
                        {
                            "id": "ab389542-53d5-346a-b168-1d915ecf0ef6",
                            "length": "257000",
                            "recording": {
                                "id": "77edd338-eeaf-4157-9e2a-5cc3bcee8abd",
                                "length": "257000",
                                "title": "Billie Jean"
                            },
                            "track_or_recording_length": "257000",
                            "position": "8",
                            "number": "8"
                        },
                        {
                            "id": "6d9e722b-7408-350e-bb7c-2de1e329ae84",
                            "length": "293000",
                            "recording": {
                                "id": "040aaffa-7206-40ff-9930-469413fe2420",
                                "length": "293000",
                                "title": "Careless Whisper"
                            },
                            "track_or_recording_length": "293000",
                            "position": "9",
                            "number": "9"
                        },
                        {
                            "id": "63b4e67c-7536-3cd0-8c47-0310c1e40866",
                            "length": "211000",
                            "recording": {
                                "id": "054942f0-4c0f-4e92-a606-d590976b1cff",
                                "length": "211000",
                                "title": "Tainted Love"
                            },
                            "track_or_recording_length": "211000",
                            "position": "10",
                            "number": "10"
                        },
                        {
                            "id": "a07f4ca3-dbf0-3337-a247-afcd0509334a",
                            "length": "245000",
                            "recording": {
                                "id": "8023b5ad-649a-4c67-b7a2-e12358606f6e",
                                "length": "245000",
                                "title": "Straight Up"
                            },
                            "track_or_recording_length": "245000",
                            "position": "11",
                            "number": "11"
                        },
                        {
                            "id": "73d47f16-b18d-36ff-b0bb-1fa1fd32ebf7",
                            "length": "322000",
                            "recording": {
                                "id": "95a8c8a1-fcb6-4cbb-a853-be86d816b357",
                                "length": "322000",
                                "title": "Black Velvet"
                            },
                            "track_or_recording_length": "322000",
                            "position": "12",
                            "number": "12"
                        }
                    ]
                }
            ],
            "asin": "B0017M8YTO"
        },
    ]
}


@pytest.fixture()
def releases():
    return _releases


@pytest.fixture()
def release_groups():
    return _release_groups


@pytest.fixture()
def artists():
    return _artists


@pytest.fixture()
def recordings():
    return _recordings
