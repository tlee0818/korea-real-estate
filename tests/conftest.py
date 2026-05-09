"""Shared fixtures for all test modules."""

import pytest

FAKE_KEY = "test_api_key_1234"
FAKE_REGION = "42820"


# ---------------------------------------------------------------------------
# Mock XML response bodies
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
