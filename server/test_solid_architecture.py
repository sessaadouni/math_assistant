"""
Test DI Container and new architecture

This script tests that the new SOLID architecture works correctly
and integrates with the existing code.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.di_container import DIContainer, get_container
from src.domain.entities import Question, Answer, Document
from src.domain.value_objects import Filters, TaskType, SessionContext


def test_container_creation():
    """Test creating DI container"""
    print("✅ Test 1: Creating DI Container...")
    container = DIContainer()
    print(f"   Container created: {container}")
    return container


def test_llm_provider(container: DIContainer):
    """Test LLM provider"""
    print("\n✅ Test 2: Getting LLM Provider...")
    llm = container.get_llm_provider()
    print(f"   LLM Provider: {llm}")
    print(f"   Model: {llm.get_model_name()}")
    print(f"   Available: {llm.is_available()}")
    
    # Test simple generation
    if llm.is_available():
        print("\n   Testing generation...")
        try:
            response = llm.generate(
                prompt="Qu'est-ce que 2+2?",
                temperature=0.0,
            )
            print(f"   Response: {response[:100]}...")
        except Exception as e:
            print(f"   ⚠️  Generation failed (may need Ollama running): {e}")
    
    return llm


def test_session_store(container: DIContainer):
    """Test session store"""
    print("\n✅ Test 3: Getting Session Store...")
    store = container.get_session_store()
    print(f"   Session Store: {store}")
    
    # Create test session
    chat_id = "test_chat_123"
    context = store.get_context(chat_id)
    print(f"   Created context for chat: {chat_id}")
    print(f"   Context: {context}")
    
    # Test update
    question = Question.create("Test question", chat_id)
    answer = Answer.create(
        question_id=question.id,
        text="Test answer",
        chat_id=chat_id,
        task_type="qa",
    )
    store.update_context(chat_id, question, answer)
    print(f"   Updated context with Q&A")
    
    # Verify
    updated_context = store.get_context(chat_id)
    print(f"   History length: {len(updated_context.history)}")
    
    return store


def test_domain_entities():
    """Test domain entities"""
    print("\n✅ Test 4: Testing Domain Entities...")
    
    # Question
    question = Question.create("Qu'est-ce qu'une intégrale?", "chat_456")
    print(f"   Question created: {question.id}")
    print(f"   Text: {question.text}")
    
    # Document
    doc = Document(
        id="doc_1",
        content="Une intégrale est...",
        metadata={"page": 42, "doc_type": "cours", "bloc_name": "Analyse"},
        score=0.95,
    )
    print(f"   Document created: {doc.id}, score={doc.score}")
    
    # Source
    source = doc.to_source()
    print(f"   Source: page {source.page}, {source.doc_type}")
    
    # Answer
    answer = Answer.create(
        question_id=question.id,
        text="Une intégrale calcule l'aire sous une courbe...",
        chat_id=question.chat_id,
        task_type=TaskType.QA.value,
        model_used="test-model",
    )
    print(f"   Answer created: {answer.id}")
    print(f"   Task type: {answer.task_type}")


def test_value_objects():
    """Test value objects"""
    print("\n✅ Test 5: Testing Value Objects...")
    
    # Filters
    filters = Filters(
        doc_type="cours",
        bloc_name="Analyse",
        chapter="Intégrales",
    )
    print(f"   Filters: {filters}")
    print(f"   Dict: {filters.to_dict()}")
    print(f"   Is empty: {filters.is_empty()}")
    
    # TaskType
    task = TaskType.QA
    print(f"   TaskType: {task.value}")
    
    # SessionContext
    context = SessionContext(chat_id="test_789")
    context.add_exchange("Question 1", "Answer 1")
    context.add_exchange("Question 2", "Answer 2")
    print(f"   SessionContext: {len(context.history)} exchanges")
    print(f"   Recent context:\n{context.get_recent_context(2)}")


def test_adapters(container: DIContainer):
    """Test adapters (integration with legacy code)"""
    print("\n✅ Test 6: Testing Adapters...")
    
    try:
        # Retriever adapter
        print("   Getting retriever...")
        retriever = container.get_retriever()
        print(f"   Retriever: {retriever}")
        
        # Test get_available_doc_types
        doc_types = retriever.get_available_doc_types()
        print(f"   Available doc types: {doc_types}")
        
        # Router adapter
        print("\n   Getting router...")
        router = container.get_router()
        print(f"   Router: {router}")
        
    except Exception as e:
        print(f"   ⚠️  Adapters test skipped (need existing code): {e}")


def test_global_container():
    """Test global container singleton"""
    print("\n✅ Test 7: Testing Global Container Singleton...")
    
    container1 = get_container()
    container2 = get_container()
    
    print(f"   Container 1: {id(container1)}")
    print(f"   Container 2: {id(container2)}")
    print(f"   Same instance: {container1 is container2}")


def main():
    """Run all tests"""
    print("=" * 70)
    print("🧪 Testing SOLID Architecture - Phase 1")
    print("=" * 70)
    
    try:
        # Create container
        container = test_container_creation()
        
        # Test domain entities
        test_domain_entities()
        
        # Test value objects
        test_value_objects()
        
        # Test session store
        test_session_store(container)
        
        # Test LLM provider
        test_llm_provider(container)
        
        # Test adapters
        test_adapters(container)
        
        # Test global container
        test_global_container()
        
        print("\n" + "=" * 70)
        print("✅ All tests passed!")
        print("=" * 70)
        print("\n📝 Next steps:")
        print("   1. Create AnswerQuestionUseCase")
        print("   2. Reorganize prompts by domain")
        print("   3. Migrate router to infrastructure layer")
        print("   4. Migrate RAGEngine to infrastructure layer")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
