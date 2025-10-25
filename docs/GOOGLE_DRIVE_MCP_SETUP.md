# Google Drive MCP Server 설치 가이드

## 개요
Google Drive MCP Server를 설치하면 Claude Desktop이 Google Drive 파일에 직접 액세스할 수 있습니다.

## 사전 요구사항
- Claude Desktop 설치
- Node.js 18+ 설치
- Google Cloud Console 계정

## 설치 방법

### 1. Google Cloud Console 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. **API 및 서비스** → **라이브러리** 이동
4. "Google Drive API" 검색 후 **사용 설정**
5. **사용자 인증 정보** → **OAuth 동의 화면** 구성
   - 사용자 유형: **외부**
   - 앱 이름, 지원 이메일 입력
   - 범위 추가: `https://www.googleapis.com/auth/drive.readonly`

6. **사용자 인증 정보 만들기** → **OAuth 클라이언트 ID**
   - 애플리케이션 유형: **데스크톱 앱**
   - 이름: "Claude MCP Google Drive"
   - **클라이언트 ID**와 **클라이언트 보안 비밀번호** 저장

### 2. MCP Server 설치

```bash
# 공식 Google Drive MCP Server
npm install -g @modelcontextprotocol/server-gdrive

# 또는 커뮤니티 버전
npm install -g google-drive-mcp
```

### 3. Claude Desktop 설정

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gdrive": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-gdrive"],
      "env": {
        "GDRIVE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GDRIVE_CLIENT_SECRET": "your-client-secret",
        "GDRIVE_REDIRECT_URI": "http://localhost:3000/oauth2callback"
      }
    }
  }
}
```

### 4. Claude Desktop 재시작

설정 파일 저장 후 Claude Desktop을 완전히 종료하고 다시 시작합니다.

### 5. OAuth 인증

첫 사용 시 브라우저가 열리면서 Google 로그인 후 권한 승인을 요청합니다.

## 사용 방법

Claude Desktop에서:
```
"내 Google Drive에서 NERD12 관련 문서 찾아줘"
"Google Docs 문서 ID 1zCOWcm6gCu0GjKEKapBfPyMQ_IpiA02EjchJgF0U96o 내용 읽어줘"
```

## 대안 MCP Servers

### 1. google-docs-mcp (더 많은 기능)
```bash
npm install -g google-docs-mcp
```

설정:
```json
{
  "mcpServers": {
    "google-docs": {
      "command": "npx",
      "args": ["-y", "google-docs-mcp"],
      "env": {
        "CLIENT_ID": "your-client-id",
        "CLIENT_SECRET": "your-client-secret",
        "REDIRECT_URI": "http://localhost:3000/oauth2callback"
      }
    }
  }
}
```

기능:
- Google Docs 읽기/쓰기
- 포맷 편집
- 전체 Drive 관리

### 2. piotr-agier/google-drive-mcp (Sheets, Slides 지원)
```bash
npm install -g @piotr-agier/google-drive-mcp
```

기능:
- Google Drive, Docs, Sheets, Slides 통합
- 파일 관리
- 보안 인증

## 트러블슈팅

### 오류: "Failed to authenticate"
- Google Cloud Console에서 OAuth 동의 화면이 올바르게 설정되었는지 확인
- CLIENT_ID와 CLIENT_SECRET이 정확한지 확인

### 오류: "Permission denied"
- Google Drive API가 활성화되었는지 확인
- OAuth 범위에 `drive.readonly` 또는 `drive`가 포함되었는지 확인

### MCP Server가 나타나지 않음
- `claude_desktop_config.json` 파일 경로 확인
- JSON 형식이 올바른지 확인 (쉼표, 중괄호 등)
- Claude Desktop 완전히 재시작

## 참고 자료

- [Official MCP Documentation](https://modelcontextprotocol.io)
- [Google Drive MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/gdrive)
- [Claude MCP Servers Directory](https://www.claudemcp.com/servers/gdrive)
- [Google Drive API Documentation](https://developers.google.com/drive/api/guides/about-sdk)

## 보안 참고사항

- OAuth 토큰은 로컬에만 저장됩니다
- Claude Desktop만 Drive 파일에 액세스할 수 있습니다
- 언제든지 Google 계정 설정에서 액세스 권한을 취소할 수 있습니다

---

작성일: 2025-10-25
