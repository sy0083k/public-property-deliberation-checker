graph TD
    %% 시작점
    START([사업 계획 수립/검토 단계]) --> Q1{<b>1단계: 사업 유형 분류</b><br>취득, 처분, 용도변경, 폐지,<br>감면, 수의매각 중 하나인가?}

    %% 1단계 분기
    Q1 -- "No" --> EXIT_NO[일반적인 관리 업무<br>심의 불필요]
    Q1 -- "Yes" --> Q2{<b>2단계: 중요재산 여부</b><br>취득/처분 10억 이상<br>또는 취득 1천㎡ / 처분 2천㎡ 이상인가?}

    %% 2단계 분기 (관리계획)
    Q2 -- "Yes (중요재산)" --> PROCESS_PLAN[공유재산관리계획 수립 대상] --> Q_EXCEPT
    Q2 -- "No" --> Q3{<b>3단계: 성격 변화/감면</b><br>용도폐지·변경, 무상 이관,<br>또는 사용료·대부료 감면인가?}

    %% 3단계 분기 (용도/감면)
    Q3 -- "Yes" --> Q_EXCEPT
    Q3 -- "No" --> Q4{<b>4단계: 서산시 특례</b><br>5,000만 원 이상 재산의<br>수의매각 가격사정인가?}

    %% 4단계 분기 (서산시 조례)
    Q4 -- "Yes" --> Q_EXCEPT
    Q4 -- "No" --> EXIT_NO

    %% 공통 필터: 심의 제외 사유 (예외 체크)
    Q_EXCEPT{<b>5단계: 심의 제외 사유</b><br>법령상 의무 취득, 토지보상법에 따른 취득,<br>동일목적 대체취득, 단순 리모델링인가?}

    %% 최종 결과
    Q_EXCEPT -- "Yes (예외 해당)" --> EXIT_EXEMPT[심의 생략 가능]
    Q_EXCEPT -- "No (예외 없음)" --> FINAL[<b>[심의 대상 확정]</b><br>공유재산심의회 상정 추진]

    %% 스타일링
    style START fill:#f9f,stroke:#333,stroke-width:2px
    style FINAL fill:#f00,stroke:#333,stroke-width:4px,color:#fff
    style EXIT_NO fill:#eee,stroke:#333
    style EXIT_EXEMPT fill:#eee,stroke:#333