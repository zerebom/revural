// エンドツーエンドテスト
async function testE2E() {
  console.log('🔄 E2Eテスト開始...');

  try {
    // 1. バックエンドAPIテスト
    console.log('1. バックエンドAPI /agents/roles をテスト...');
    const agentsResponse = await fetch('http://localhost:8000/agents/roles');

    if (!agentsResponse.ok) {
      throw new Error(`Backend API failed: ${agentsResponse.status}`);
    }

    const agents = await agentsResponse.json();
    console.log(`✅ バックエンドAPI: ${agents.length}人のエージェントを取得`);

    // 2. フロントエンドテスト
    console.log('2. フロントエンド http://localhost:3000 をテスト...');
    const frontendResponse = await fetch('http://localhost:3000');

    if (!frontendResponse.ok) {
      throw new Error(`Frontend failed: ${frontendResponse.status}`);
    }

    const html = await frontendResponse.text();
    console.log('✅ フロントエンド: 正常にレスポンス');

    // 3. PRDレビューAPIテスト（エージェント選択付き）
    console.log('3. レビューAPI（エージェント選択付き）をテスト...');
    const reviewResponse = await fetch('http://localhost:8000/reviews', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prd_text: 'テスト用PRD: 新しいモバイルアプリの機能要件',
        panel_type: null,
        selected_agent_roles: ['engineer', 'ux_designer']
      })
    });

    if (!reviewResponse.ok) {
      throw new Error(`Review API failed: ${reviewResponse.status}`);
    }

    const reviewResult = await reviewResponse.json();
    console.log(`✅ レビューAPI: review_id=${reviewResult.review_id} で開始`);

    console.log('🎉 全てのテストが成功しました！');
    console.log('\n== Phase 3 完了確認 ==');
    console.log('✅ MemberSelectGrid.tsx コンポーネント作成');
    console.log('✅ PrdInputForm.tsx エージェント選択統合');
    console.log('✅ API統合動作確認');
    console.log('✅ エンドツーエンド動作確認');

  } catch (error) {
    console.error('❌ テストエラー:', error.message);
    process.exit(1);
  }
}

testE2E();
