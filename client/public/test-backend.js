// Test simple pour vérifier la connectivité backend
async function testBackend() {
  const baseUrl = 'http://localhost:8000';
  
  console.log('🧪 Test de connectivité backend...');
  
  // Test 1: Health check
  try {
    console.log('1️⃣ Test /health...');
    const res = await fetch(`${baseUrl}/health`);
    const data = await res.json();
    console.log('✅ Health check OK:', data);
  } catch (e) {
    console.error('❌ Health check FAILED:', e);
    return;
  }
  
  // Test 2: RAG check
  try {
    console.log('2️⃣ Test /rag_check...');
    const res = await fetch(`${baseUrl}/rag_check`);
    const data = await res.json();
    console.log('✅ RAG check OK:', data);
  } catch (e) {
    console.error('❌ RAG check FAILED:', e);
  }
  
  // Test 3: SSE streaming (chat)
  try {
    console.log('3️⃣ Test /chat (SSE)...');
    const url = `${baseUrl}/chat?question=test&k=3`;
    const res = await fetch(url, {
      headers: { 'Accept': 'text/event-stream' }
    });
    
    if (!res.ok) {
      console.error('❌ Chat request failed:', res.status, res.statusText);
      return;
    }
    
    console.log('✅ Chat request OK, reading stream...');
    
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let receivedTokens = 0;
    
    // Lire seulement quelques chunks pour le test
    for (let i = 0; i < 5; i++) {
      const { done, value } = await reader.read();
      if (done) break;
      const text = decoder.decode(value);
      receivedTokens++;
      console.log(`📥 Chunk ${receivedTokens}:`, text.substring(0, 50) + '...');
    }
    
    reader.cancel();
    console.log(`✅ SSE streaming OK (received ${receivedTokens} chunks)`);
    
  } catch (e) {
    console.error('❌ Chat streaming FAILED:', e);
  }
  
  console.log('🏁 Tests terminés!');
}

// Pour utiliser dans la console du navigateur:
// testBackend()

if (typeof window !== 'undefined') {
  window.testBackend = testBackend;
  console.log('💡 Tapez testBackend() dans la console pour tester la connectivité');
}
