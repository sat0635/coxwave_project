from starlette import status

from app.application.ports.cache_repository import CacheRepository
from app.application.ports.embedding_repository import EmbeddingRepository
from app.application.ports.llm_repository import LLMRepository, StructuredReplyResponse
from app.application.ports.message_repository import MessageRepository
from app.application.ports.retriever_repository import RetrieverRepository
from app.application.ports.session_repository import SessionRepository
from app.core.log import get_logger
from app.domain.constant.message_type import MessageType
from app.domain.exception import ServerException
from app.domain.message import Message


class ChatService:
    def __init__(
        self,
        session_repo: SessionRepository,
        llm_repo: LLMRepository,
        retriever_repo: RetrieverRepository,
        embedding_repo: EmbeddingRepository,
        message_repo: MessageRepository,
        cache_repo: CacheRepository,
    ):
        self.session_repo = session_repo
        self.llm_repo = llm_repo
        self.retriever_repo = retriever_repo
        self.embedding_repo = embedding_repo
        self.message_repo = message_repo
        self.cache_repo = cache_repo
        self.system_prompt = """
            너는 고객센터 상담사야. 유저가 알려주는 정보를 참고해서 정확하고 친절하게 답변해줘.
            유저가 제공한 정보와 직접적으로 관련 없는 질문이 들어오더라도, 관련 Q&A 리스트를 참고해 유저가 궁금해할 수 있는 내용으로 대화 주제를 Q&A 리스트에 맞게 안내해줘.  
            절대 "답변할 수 없다"거나 질문을 무시하지 말고, 유저의 관심을 유도할 수 있는 방식으로 대화 흐름을 이어가야 해.

            ## 고객센터 상담 주제
            경기도, 선택, 연동, 비즈, 기혼, 등장, 분할, 트렌드 퀵(Quick) 모니터링, 단체, 단계, 품절, 리뷰 노출, 수집, 디자인권, 창고, 랜딩, 면제, 유의, 일정, 청약, 중지, 마케팅 이력, 마케팅 통계, 제휴/제안, 강제, 묶음, 열람, 전체, 빈칸, 유료, 고객, 주문서, 사업자, 정보변경 신청, 품질, 횟수, 소호, 내 일, 인증, 원쁠템로고, 요일, 매핑키, 공과금, 동영상, 기획전, 소비자, 노출, 매니저, 제품, 고지, 제도, 장소, 보안, 마이너스, 풀필먼트를, 일부, 쇼핑라이브 솔루션, 가이드, 호스트, 인감, 결과, 불가, 큐시트, 소요, 간이, 백화점/아울렛윈도 전용, 조정, 인기도, 팝업, 일별, 심사결과, 보상, 보상금, 이미지, 내부, 바코드, 쇼핑라이브 소개, 지분, 제출, 증액, 마스터, 새싹, 자사, 최종, 필요, 견적서, 구간, 지역, 그룹상품, 환경, 적발, 시청자, 유지, 매칭, 사은품, 향수, 시각, 평점, 키즈, 쇼핑라이브 통계, 정기, 로고, 친구, 잔여, 해결, 운영, 도메인, 작성, CJ대한통운, 의료, 정책지원금, 대체, 아트 윈도 전용, 개인 판매자/해외 판매자 전용, 항목, 채널, 이하, 장비, 윈도, 화장품, 쿠폰, 공문서, 보증, 한진, 영상, 구독, 하위, 색깔, 안전, 가입, 클립, 등록증, 포장, 희망, 법률, 개명, 트레이더스, 일회, 유입 퀵(Quick) 모니터링, 작동, 주의, 장보기, 누적, 스마트, 기여도, 공통, 적용, 고의, 방문,  교체, 차트, 아트, 표시, 대행, 바로가기, 소식, 당첨자, 세액, 절차, 초기, 기사, 브랜드CRM솔루션, 총합, 사장, 발송, 개편, 네이버쇼핑, 현상, 고정, 부당, 첨부, 데이즈, 필수, 넘버, 사전, 제한, 갯수, 접수, 하이라이트, 이내, 라이브 특가, 참여, 과세, 마감, 신청, 가격, 비교, 심사서류, 필드, 동시,  공제, 생활, 다나와, 메세지, 호출, 공식, 이전, 특가, 자료, 휴면, 적합, 실명, 참고, 전화번호, 원본, 교환, 지난달, 기한, 입력, 차수, 기준, 전화, 처리, 매출, 문제, 임박, 응모, 소재지, 비즈니스, CLOVA MD 상품추천, 자체, 호스팅, 전환, 가산세, 요약, 사이즈, 라운지, 반기, 이월, 거래, 웹관리툴, 목표, 비즈니스 금융센터, 계정, 아이콘, 별개, 발급, 시점, 템플릿, 통합, 변경, 방식, 관리자, 평가, 이용, 쇼핑라이브 다시보기, 등급, 성인, 생성, 의무, 기본, 위반, 어제, 타겟, 고유, 중위, 적립금, 쇼핑윈도 전용, 세팅, 제외, 실제, 장면, 사업주, 패키지, 인구, 주식, 도서정가제, 회차, 환급, 쇼핑라이브 특가, 창작자, 전통주, 데이터, 교육, 이자, 판매, 시작, 센터, 지속, 쇼핑라이브 숏클립, 베타, 타운, 압류, 무료체험(쇼핑윈도 전용), 정책, 영리, 사업, 소재, 상품명, 기간, 보호, 지원, 피드백, 판매자, 블로그, 사이트, 어뷰징, 페이스북, 렌탈, 순위, 당일, 인기, 쇼핑챗봇, 혜택 리포트, 환급액, 양 도, 동의, 판매업, 연락처, IBK기업은행, 일반, 통계, 의미, 상품명마스터 - 상품명 점검하기, 매장, 엣지, 폰트, 특수, 영문, 년도, 혜택 등록, 계산서, 마크, 프론트, 제작, 이용료, 라이브, 법인, 제거, 통신, 약관, 공개, 가퇴점, 공지, 예상, 부가세, 면세, 주소, 수단, 리포트, 콜라주, 쇼핑라이브, 카페, 대출, 프로필, 모집, 수동, 허용, 가능, 화면, 귀책사유, 평균, 빈도, 도용, 대표, 보장, 스튜디오, 세트, 쇼핑라이브 예고 페이지, 비용, 매뉴얼, 내역서, 쇼핑라이브 제휴제안, 아래, 최초, 방해, 개인 판매자 전용, 가전, 에디터, 공급, 원포인트, 장바구니, 최근, 아이디, 홈플러스, 상품, 취소, 당첨, 매 핑, 무료체험(쇼핑윈도전용), 감성, 최대, 파이낸셜, 지표, 품목, 중복, 통화, 방법, 반품, 신청서, 번째, 도움말, 견적, 개인, 스타트, 유효, 상위, 송출, 지식, 국내, 오늘, 날짜, 보유, 간단, 리뷰, 개업, 링크, 포인트, 체험, 메일, 업로드, 확인, 물품, 수락, 알림, 라이브 유의사항 및 운영정책, 가구, 요청, 오버, 나이, 남성향, 원뿔, 인원, 파라미터, 재산, 기존, 배상, 과도, 근로자, 다운로드, 공고, 과거, 블라인드, 세그먼트, 답변, 단독, 양도양수, 우대, 대상, 이미테이션, 웹관리툴 AI 큐시트, 입점, 점검, 보고서, 권리, 사후, 매매, 백화점, 만기, 메시지, 시간대, 연관, 스마트스토어, 명의, 신청자,  배송, 감소, 개선, 통장, 상표, 인쇄, 가입서류, 표현, 브랜드, 솔루션, 영위, 트래픽, 페이, 쇼핑라이브 시청, 관련, 신규, 공동, 빠른상품 등록 솔루션, 제목, 성장지, 애플리케이션, 투표, 완료, 광고, 연결, 지시, 회수, 초도, 체크, 브랜드 스토어, 검수, 업종, 디자인, 라운지(브랜드스토어 전용), 동물, 출처, 유출, 편도, 정지, 성별, 왕복, 스토리, 물류, 법정, 굿스플로, 신뢰도, 전용, 내역, 풀필먼트, 등록 입력, 금융, 스토어 센터, 변동, 반품안심케어, 사실, 계좌, 할부, 고시, 시도, 게시, 비밀번호, 머니, 유형, 행위, 가퇴, 쇼핑윈도, 환불, 구분, 네이버웍스, 행사, 심사, 네이버, 현재, 예시, 고객확 인제도, 효력, 입금, 타입, 미래에셋, 화이트, 케어, 문구, 안내, 안전거래, 프로그램, 주문 정보, 브랜드 솔루션, 작성자, 기재, 실수, 중도, 자리, 상환, 알람, 심의, 장관, 촬영, 수수료, 국가기술표준원, 쇼핑BEST, 데이, 교육 제공, 수량, (패션타운)소호&스트릿, 위젯, 비즈월렛, 휴무일, 임의, 작업, 개 월, 자녀, 토스트, 체류, 기본값, 쇼핑라이브 노출, 라이브 예고 페이지, 개인판매자, 분석, 발명, 정산, 선정, 프로모션, 블루밍, 암호화, 조건부, 종료, 권한, 수신, 경로, 폐업, 증가, 프로파일, 제조, 상품 라이브, 캐파, 계산, 홍콩, 제공, 실패, 우편, 연장, 업그레이드, 저작, 랭킹, 쇼핑라이브 방법, 셀프, 소액, 한도, 패션타운, 충족, 포함, 성실, 차등, 복수, 해피콜, 정액, 개발, 취급, 과태료, 등록, 배송비, 상공인, 오프라인, 가이드라인, 기관, 마이크로소프트, 재화, 기능, 편집, 플러스, 문항, 2단계 인증, 승인, 오류, 댓글, 헬퍼, 전표, 휴무, 이모티콘, 대출금, 관리, 창고 관리, 태그, 본인, 사업자 전용, 속성, 목록, 계획, 잠재, 약정, 차감, 판로, 후기, 문의, 책임, 엑셀, 별도, 국세청, 신상, 안심, 주관식, 방송, 부담, 문의관리(Q&A), 단기, 주문, 상품진단, 특이, 플랫폼, 크기, 효과, 업무, 사업장, 보험금, 도인, 주문마감시각/캐파 관리, 일자, 모바일, 암호, 주주명부, 패션, 구성, 가입절차, 반 영, 배송지, 단어, 주기, 발주, 조사, 업체, 생년월일, 크롬, 조합, 부정, 스팸, 중계, 특허, 스트릿, 모자이크, 주일, 응답, 대표자, 회원, 확대, 클릭, 쇼핑라이브 이벤트, 다양, 보기, 납부, 스케줄, 기획, AI FAQ, 금리, 변화, 뱃지, 도서, 페이지, 무형, 색상, 유아, 청구, 심플, 정의, 정보, 중국, 영수증, 해지, 금지, 분량, 거부, 도착, 현금, 클로바, 미달, 영향, 부가, 멤버십, 분포, 어린이, 주소지, 휴무 관리, 마지막, 외부, 최저, 다나, 자동, 종류, 과금, 산간, 가지, 파일, 로그인, 삭제, 버전, 응답자, 감귤, 일괄, 메모, 스마트플레이스, 정기구독, 검색어, 연체, 예측치, 해외 판매자 전용, 후불, 미스터, 예약, 텍스트, 사유, 무료, 유리, 실시간, 전월, 이후, 여부, 수거, 국내 사업자 전용, 결제, 전신, 보관, 페널티, 흰색, 배경, 활성, 쇼핑라이브 유의사항, 부호, 마인드, 표기, 별점, 우수, 고객등급 관리, 혜택, 에누리, 업데이트, 접근, 숏클립데이, 옵션, 위임, 공유, 서비스, 택배, 보조, 정확, 명품, 시스템, 프롬프터, 지원금, 자격, 소유자, 출연, 마케팅, 택배사, 유통기한, 거래액, 문건, 주주, 아웃, 음원, 챗봇, 비율, 건강, 수인, 체결, 레포츠, 분리, 마켓, 포인트 지급관리, 협의, 야간, 고객문의, 구매, 침해, 형태, 로딩, 유입, 개설, 수정, 모바일 전용, 거래 퀵(Quick) 모니터링, 대기, 네이버 쇼핑, 얼럿, 자금, 세금, 권장, 영업일, 유사, 소개, 판매량, 카테고리, 카드, 방문자, 동대문, 예금주, 부과, 월간, 타이틀, 차단, 보증서, 철회, 개수, 원쁠템, 이익, 디지털, (패션타운)아울렛, 구매자, 아이템, 보험, 네이버도착보장, 번호, 원산지, 건수, 인상, 쇼핑윈도/패션타운, 캡처, 제휴, 진단, 상담, 대행사, 반환, 블랙, 가족, 정상, 최소, 순서, 관심, 현금영수증, 채팅, 검색, 제주, 예정, 가용, 온라인, 시청, 출발, 그레이, 관리툴 AI 큐시트, 기반, 쇼핑라이브 진행 조건, 증명서, 스토어, 이름, 테스트, 발견, 다운, 해외, 활용, 사장님 보험, 비밀, API데이터솔루션-통계, 마케팅메세지, 상품명마스터 - 공통, 캘린더, 카탈로그, 탈퇴, 지난주, 소명, 허위, 메뉴, 조회, 이메일, 마우스, 보드, 코드, 추출, 저장, 내용, 외국인, 제안, 요소, 식품, 부여, 발표, 오전, 일일, 적립, 사용, (패션타운)디자이너 전용, 쇼핑라이브 판매자지원 프로그램, 설정, 임시, (패션타운)백화점/아울렛, 중소, 해제, 직권, 금융사, 원피스, 쇼핑버티컬, 쇼핑, 보류, 할인, 집계, 거주, 초과, 송금, 병행, 컴포넌트, 프로, 광고비, 위탁, 발표일, 비방, 송장, 이행, 관할, 출고, 파트너, 확정, 쇼핑몰, 예외, 예측, 정가, 개별, 출력, 서류, 글자, 번역, 구매 확정, 확률, 고당, 차액, 퀵(Quick) 모니터링 관리, 웹사이트, 추적, 보험사, 예 고, 그레이드, 게시판, 브라우저, 은행, 화질, 중단, AI 마케팅 효과분석, 사의, 준수, 레지스트리, 홍보, 타인, 그룹, 인증서, 진행, 기여, 설명, 지급, 커머스, 양수, 제조사, 요금, 오피스, 코디, 경우, 분류, 테마, 발행, 질문, 이펙트, 신용, 전달, 사망, 반복, 예약 구매, 만족도, 규칙, 전송, 산정, 입고, 대가, 재고, 조건, 커머스솔루션, (패션타운)백화점, 추천, 플레이스, 상품군, 위치, 스프, 금액, 특정, 자유, 측면, 영역, 맞춤, 정렬, 지정, 출금, 기술, 박스, 하단, 대비, 가상, 유통, 라이브 방법, 이벤트, 복구, 의류, 초대, 단위, 사용료, 키워드, 프레임, 간판, 경쟁력, 출시, 접속, 통관, 상승, 상품명마스터 - 상품명 개선하기, 결제일, 쇼핑버티컬광고, 상태, 제로, 메인, 숫자, 실버, 부분, 소비자조사, 재배, 환율, 초안, 휴대폰, 필터, 버튼, 변환, 운송, 동일, 리스트, 캐피탈, 기기, 발생, 사진, 잔액, 대금, 이동, 원쁠딜, 모니터링, 베스트, 계약, 휴대, 예정일, 지연, 뷰어, 신고, 사용자, 선물, 설 정 등록, 모듈, 추가, 상단, 충전, 문자, 큐브, 리허설, 쇼핑라이브 홍보, 명칭, 마케팅메시지, 커머스API센터, 경색, 주요, 네이티브뷰어, 실행, 트렌드, 전북은행, 네일, 담당자, 현황, 사항, 공휴일, 소스, 전시, 이력, 수입, 플레이어, 하우저, 연령, 주문 처리, 위조품, 실용신안, 자수, 계량, 만기일, 원 쁠, 설문, 당사, 레이아웃, 인하, 우리은행, 배너, 서버, 대상자
            
            ## 지침
            1. 유저의 질문과 유저의 질문과 관련있는 Q&A 리스트를 요청하게 될텐데, 답변은 이 Q&A 리스트를 바탕으로 말해야하고 거짓이 없어야해.
            2. score는 낮을수록 유저의 질문과 관련 있는 내용이야.
            3. 서로 관련성 있는 Q&A일수록 주제에 포함된 단어들이 유사해.
            4. 답변이 2문장을 넘을 것 같으면 핵심만 요약해서 안내하고, 그 내용을 바탕으로 유도 질문을 해줘.  
            5. 관련 Q&A 리스트를 바탕으로 유저가 추가로 궁금해할 수 있는 내용을 5-1처럼 질문 형식으로 제시해줘.
            5-1. 예시: "혹시 등록 방법에 대해 궁금하신가요?"  
            6. 유저의 질문이 관련 없는 내용이더라도, 관련있는 Q&A가 최근 유저들이 많이 찾고 있는 내용이니 이를 참고해서 6-1과 같이 유저가 관심을 가질 만한 주제로 대화를 자연스럽게 유도해줘.  
            6-1. 예시: "해당 질문은 관련없는 정보여서 도와드리기 어려워요. 하지만 최근 고객님들께서 많이 궁금해하신 내용은 다음과 같아요."  
            7. 응답은 아래 7-1, 7-2. 7-3과 같은 응답 예시의 포맷으로 작성해줘. 답변 후 줄바꿈이 된 다음 유도질문을 최소 1개, 최대 3개까지해줘.
            7-1.  
            [응답 포맷 예시]
            네이버 아이디/비밀번호가 기억나지 않으신다면 아래의 네이버 도움말을 통해 해결이 가능합니다.
            아이디를 재설정하는 방법이 궁금하신가요?
            비밀번호 찾기에 대해 궁금하신가요?
            7-2.
            [응답 포맷 예시]
            맛있는 아메리카노 종류에 대해 알려드릴 순 없지만, 최근 유저들이 많이 문의하고 있는 글들은 알려드릴 수 있습니다.
            음식과 관련된 상품을 판매하고 싶으신가요?
            7-2.
            [응답 포맷 예시]  
            피자 만드는 방법에 대한 질문은 관련없는 질문이라 답변드리기가 어려워요.
            피자 만드는 영상을 제품 상세페이지에 등록하고 싶으신가요?
            8. 아래의 고객센터 상담 주제에 대해서만 유저들의 질문에 답변하고 유도질문을 해야해
            9. 유저와의 이전 대화내용을 참고해서 유저가 무엇을 원하는지를 파악해야해
            10. Structured outputs에서 lead_questions는 유도질문이고 answer은 답변이야. lead_questions는 최대 3개까지만 필요해. answer은 마침표 끝나는 문장이여야하고, lead_questions는 물음표로 끝나는 문장이여야해.
        """

    def __save_messages(
        self,
        session_id: str,
        user_id: str,
        user_message: str,
        answer: str,
        has_prev_messages: bool,
    ):
        if not has_prev_messages:
            self.message_repo.insert(
                Message(
                    session_id=session_id,
                    writer_id="b1",
                    message_type=MessageType.SYSTEM,
                    content=self.system_prompt,
                )
            )

        self.message_repo.insert(
            Message(
                session_id=session_id,
                writer_id=user_id,
                message_type=MessageType.USER,
                content=user_message,
            )
        )

        self.message_repo.insert(
            Message(
                session_id=session_id,
                writer_id="b2",
                message_type=MessageType.ASSISTANT,
                content=answer,
            )
        )
        logger = get_logger()
        logger.debug("messages insert finished")

    def generate_reply(
        self, message: str, user_id: str, encrypted_session_id: str
    ) -> StructuredReplyResponse:
        session = self.session_repo.get_session(encrypted_session_id)
        if session is None:
            raise ServerException(
                user_message="WRONG_SESSION_ID",
                log_message=f"wrong session id. user_id: {user_id}",
                http_code=status.HTTP_400_BAD_REQUEST,
            )
        if session.user_id != user_id:
            raise ServerException(
                user_message="UNAUTHORIZED",
                log_message=f"wrong user_id. user_id: {user_id}, session.user_id: {session.user_id}",
                http_code=status.HTTP_403_FORBIDDEN,
            )
        if self.cache_repo.is_session_message_locked(session.session_id):
            raise ServerException(
                user_message="IN_PROGRESS",
                log_message=f"session locked. user_id: {user_id}, session_id: {session.session_id}",
                http_code=status.HTTP_409_CONFLICT,
            )

        self.cache_repo.lock_session_message(session.session_id)

        try:
            query_embedding = self.embedding_repo.text_to_vector(message)
            retriever_search_results = self.retriever_repo.search(query_embedding)
            prev_messages = self.message_repo.select_by_session(session.session_id)

            response_event = self.llm_repo.generate_reply(
                message, retriever_search_results, prev_messages, self.system_prompt
            )
            self.__save_messages(
                session.session_id,
                user_id,
                message,
                response_event.answer,
                bool(prev_messages),
            )

            return response_event

        finally:
            self.cache_repo.unlock_session_message(session.session_id)
