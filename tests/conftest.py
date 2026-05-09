"""Shared fixtures and XML/JSON response bodies for all test modules."""

FAKE_KEY = "test_api_key_1234"
FAKE_REGION = "42820"

# ---------------------------------------------------------------------------
# Mock XML / JSON response bodies
# ---------------------------------------------------------------------------

SALES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header><resultCode>00</resultCode><resultMsg>OK</resultMsg></header>
  <body>
    <items>
      <item>
        <dealYear>2024</dealYear>
        <dealMonth>3</dealMonth>
        <dealDay>15</dealDay>
        <siGunGu>고성군</siGunGu>
        <umdNm>대진리</umdNm>
        <jibun>123</jibun>
        <landCdNm>임</landCdNm>
        <area>500.0</area>
        <dealAmount>5,000</dealAmount>
        <landUse>계획관리지역</landUse>
        <buyerGbn>개인</buyerGbn>
        <cdealType></cdealType>
      </item>
    </items>
    <totalCount>1</totalCount>
    <pageNo>1</pageNo>
    <numOfRows>10</numOfRows>
  </body>
</response>
"""

COMMERCIAL_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header><resultCode>00</resultCode><resultMsg>OK</resultMsg></header>
  <body>
    <items>
      <item>
        <dealYear>2024</dealYear>
        <dealMonth>3</dealMonth>
        <dealDay>15</dealDay>
        <siGunGu>고성군</siGunGu>
        <umdNm>대진리</umdNm>
        <buildingUse>상업용</buildingUse>
        <landArea>300.0</landArea>
        <buildingArea>150.0</buildingArea>
        <floors>3</floors>
        <buildYear>2010</buildYear>
        <dealAmount>15,000</dealAmount>
      </item>
    </items>
    <totalCount>1</totalCount>
    <pageNo>1</pageNo>
    <numOfRows>10</numOfRows>
  </body>
</response>
"""

PERMIT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header><resultCode>00</resultCode><resultMsg>OK</resultMsg></header>
  <body>
    <items>
      <item>
        <platPlc>고성군 대진리 100</platPlc>
        <archGbCdNm>신축</archGbCdNm>
        <mainPurpsCdNm>주택</mainPurpsCdNm>
        <platArea>200.0</platArea>
        <archArea>120.0</archArea>
        <vlRat>60.0</vlRat>
        <bcRat>50.0</bcRat>
        <pmsDay>20240301</pmsDay>
        <stcnsDay>20240401</stcnsDay>
        <useAprDay>20241201</useAprDay>
      </item>
    </items>
    <totalCount>1</totalCount>
  </body>
</response>
"""

TRENDS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header><resultCode>00</resultCode><resultMsg>OK</resultMsg></header>
  <body>
    <items>
      <item>
        <period>202403</period>
        <regionNm>고성군</regionNm>
        <indexValue>101.5</indexValue>
        <changeRateMom>0.3</changeRateMom>
        <changeRateYoy>2.1</changeRateYoy>
      </item>
    </items>
    <totalCount>1</totalCount>
  </body>
</response>
"""

APPRAISED_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header><resultCode>00</resultCode><resultMsg>OK</resultMsg></header>
  <body>
    <items>
      <item>
        <sigCd>42820</sigCd>
        <emdCd>대진리</emdCd>
        <mnnmSlno>123-1</mnnmSlno>
        <lndpclAr>500.0</lndpclAr>
        <pblntfPclnd>50000</pblntfPclnd>
        <stdrYear>2024</stdrYear>
      </item>
    </items>
    <totalCount>1</totalCount>
  </body>
</response>
"""

STANDARD_PRICE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header><resultCode>00</resultCode><resultMsg>OK</resultMsg></header>
  <body>
    <items>
      <item>
        <sigunguCd>42820</sigunguCd>
        <umdNm>대진리</umdNm>
        <jibun>100</jibun>
        <lndcgrCodeNm>임</lndcgrCodeNm>
        <lndpclAr>1000.0</lndpclAr>
        <pblntfPclnd>30000</pblntfPclnd>
        <stdrYear>2024</stdrYear>
        <prposAreaDstrcNm>계획관리지역</prposAreaDstrcNm>
        <lndUse>임야</lndUse>
        <tpgrphHgCodeNm>평지</tpgrphHgCodeNm>
        <roadSideCodeNm>맹지</roadSideCodeNm>
      </item>
    </items>
    <totalCount>1</totalCount>
  </body>
</response>
"""

ZONING_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header><resultCode>00</resultCode><resultMsg>OK</resultMsg></header>
  <body>
    <items>
      <item>
        <sigunguCd>42820</sigunguCd>
        <umdNm>대진리</umdNm>
        <jibun>123-1</jibun>
        <lndcgrCodeNm>임</lndcgrCodeNm>
        <prposAreaDstrcNm>계획관리지역</prposAreaDstrcNm>
        <prposAreaDstrcNo>ZN001</prposAreaDstrcNo>
        <lndpclAr>500.0</lndpclAr>
      </item>
    </items>
    <totalCount>1</totalCount>
  </body>
</response>
"""

REGISTRY_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header><resultCode>00</resultCode><resultMsg>OK</resultMsg></header>
  <body>
    <items>
      <item>
        <platPlc>고성군 대진리 100-5</platPlc>
        <bldNm>테스트건물</bldNm>
        <mainPurpsCdNm>단독주택</mainPurpsCdNm>
        <strctCdNm>목조</strctCdNm>
        <grndFlrCnt>2</grndFlrCnt>
        <ugrndFlrCnt>0</ugrndFlrCnt>
        <totArea>150.0</totArea>
        <useAprDay>20100315</useAprDay>
        <pmsDay>20091201</pmsDay>
        <archGbCdNm>신축</archGbCdNm>
        <prposAreaDstrcNm>계획관리지역</prposAreaDstrcNm>
      </item>
    </items>
    <totalCount>1</totalCount>
  </body>
</response>
"""

ADDRESS_JSON = """{
  "results": {
    "common": {
      "totalCount": "1",
      "errorCode": "0",
      "errorMessage": "정상"
    },
    "juso": [
      {
        "roadAddr": "강원특별자치도 고성군 대진항길 12",
        "jibunAddr": "강원특별자치도 고성군 현내면 대진리 123",
        "zipNo": "24763",
        "siNm": "강원특별자치도",
        "sggNm": "고성군",
        "emdNm": "대진리",
        "rn": "대진항길",
        "buildMnnm": "12",
        "buildSlno": "0",
        "bdMgtSn": "4282025300100010000000001",
        "admCd": "4282025300",
        "bdNm": "",
        "mtYn": "0",
        "x": "128.37",
        "y": "38.58"
      }
    ]
  }
}"""

RATE_LIMIT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header><resultCode>22</resultCode><resultMsg>일일 호출 한도 초과</resultMsg></header>
  <body></body>
</response>
"""

INVALID_KEY_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header><resultCode>30</resultCode><resultMsg>인증키 오류</resultMsg></header>
  <body></body>
</response>
"""

# REB-format XML fixtures (SttsApiTbl* response structure)

REB_DATA_XML = """<?xml version="1.0" encoding="UTF-8"?>
<SttsApiTblData>
  <head>
    <list_total_count>1</list_total_count>
    <RESULT>
      <CODE>INFO-000</CODE>
      <MESSAGE>정상 처리되었습니다.</MESSAGE>
    </RESULT>
  </head>
  <row>
    <STATBL_ID>TBL_LND_CHGRT</STATBL_ID>
    <DTACYCLE_CD>MM</DTACYCLE_CD>
    <DTA_VAL>101.5</DTA_VAL>
  </row>
</SttsApiTblData>
"""

REB_STATS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<SttsApiTbl>
  <head>
    <list_total_count>1</list_total_count>
    <RESULT>
      <CODE>INFO-000</CODE>
      <MESSAGE>정상 처리되었습니다.</MESSAGE>
    </RESULT>
  </head>
  <row>
    <STATBL_ID>A_2024_00900</STATBL_ID>
    <STATBL_NM>(연) 지역별 지가지수</STATBL_NM>
  </row>
</SttsApiTbl>
"""

REB_RATE_LIMIT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<SttsApiTblData>
  <head>
    <list_total_count>0</list_total_count>
    <RESULT>
      <CODE>ERROR-337</CODE>
      <MESSAGE>일별 트래픽 제한을 넘은 호출입니다.</MESSAGE>
    </RESULT>
  </head>
</SttsApiTblData>
"""

REB_INVALID_KEY_XML = """<?xml version="1.0" encoding="UTF-8"?>
<SttsApiTblData>
  <head>
    <list_total_count>0</list_total_count>
    <RESULT>
      <CODE>ERROR-290</CODE>
      <MESSAGE>인증키가 유효하지 않습니다.</MESSAGE>
    </RESULT>
  </head>
</SttsApiTblData>
"""

EMPTY_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <header><resultCode>00</resultCode><resultMsg>OK</resultMsg></header>
  <body>
    <items></items>
    <totalCount>0</totalCount>
  </body>
</response>
"""
