import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const MindFlowApp());
}

class MindFlowApp extends StatelessWidget {
  const MindFlowApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MindFlow',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primaryColor: const Color(0xFF7EB5A6),
        scaffoldBackgroundColor: const Color(0xFFF8F9FA),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF7EB5A6),
          primary: const Color(0xFF7EB5A6),
          secondary: const Color(0xFFB8D4E3),
        ),
        useMaterial3: true,
      ),
      home: const ChatScreen(),
    );
  }
}

// ============================================
// API SERVICE - Kết nối với FastAPI Backend
// ============================================
class MindFlowApiService {
  // ⚠️ ĐỊA CHỈ BACKEND - Chọn đúng theo cách bạn chạy Flutter:
  // Android Emulator: http://10.0.2.2:8000
  // iOS Simulator: http://localhost:8000
  // Điện thoại thật: http://192.168.1.XX:8000 (IP máy tính)
  // Web browser: http://localhost:8000
  static const String baseUrl = 'https://mindflow-3zph.onrender.com';

  static Future<String> sendMessage(
    String userId,
    String message,
    List<Map<String, String>> history,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/chat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_id': userId,
          'message': message,
          'history': history.map((h) => {
            'role': h['role'] == 'user' ? 'user' : 'assistant',
            'content': h['text'] ?? h['content'] ?? '',
          }).toList(),
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['reply'] ?? 'Xin lỗi, mình không hiểu.';
      } else {
        return '⚠️ Lỗi kết nối: ${response.statusCode}';
      }
    } catch (e) {
      return '⚠️ Không thể kết nối đến MindFlow Backend.\nĐảm bảo server đang chạy!';
    }
  }
}

// ============================================
// CHAT SCREEN
// ============================================
class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<Map<String, String>> _messages = [
    {
      'role': 'ai',
      'text': 'Xin chào! Mình là MindFlow 🧠✨\nHôm nay bạn cảm thấy thế nào?'
    }
  ];
  
  final List<Map<String, String>> _history = [];
  final TextEditingController _controller = TextEditingController();
  bool _isLoading = false;
  
  // User ID cố định (sau này có thể dùng UUID hoặc device ID)
  final String _userId = 'user_001';

  Future<void> _sendMessage() async {
    if (_controller.text.trim().isEmpty || _isLoading) return;

    final userMessage = _controller.text.trim();
    
    setState(() {
      _messages.add({'role': 'user', 'text': userMessage});
      _isLoading = true;
    });
    
    _controller.clear();

    // Gọi API thật
    final aiResponse = await MindFlowApiService.sendMessage(
      _userId,
      userMessage,
      _history,
    );

    setState(() {
      _messages.add({'role': 'ai', 'text': aiResponse});
      _isLoading = false;
      
      // Cập nhật lịch sử
      _history.add({'role': 'user', 'content': userMessage});
      _history.add({'role': 'assistant', 'content': aiResponse});
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'MindFlow ',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w600,
          ),
        ),
        backgroundColor: const Color(0xFF7EB5A6),
        centerTitle: true,
        elevation: 0,
      ),
      body: Column(
        children: [
          // Khu vực hiển thị tin nhắn
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                final isUser = message['role'] == 'user';

                return Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 12,
                    ),
                    decoration: BoxDecoration(
                      color: isUser ? const Color(0xFF7EB5A6) : Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.05),
                          blurRadius: 10,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Text(
                      message['text']!,
                      style: TextStyle(
                        color: isUser ? Colors.white : Colors.black87,
                        fontSize: 16,
                        height: 1.4,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),

          // Loading indicator
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF7EB5A6)),
                    ),
                  ),
                  SizedBox(width: 8),
                  Text(
                    'MindFlow đang suy nghĩ...',
                    style: TextStyle(
                      color: Color(0xFF7EB5A6),
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),

          // Khu vực nhập tin nhắn
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.05),
                  blurRadius: 10,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    enabled: !_isLoading,
                    decoration: InputDecoration(
                      hintText: 'Chia sẻ cảm xúc của bạn...',
                      hintStyle: TextStyle(color: Colors.grey[400]),
                      filled: true,
                      fillColor: const Color(0xFFF0F4F3),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(30),
                        borderSide: BorderSide.none,
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 14,
                      ),
                    ),
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  decoration: BoxDecoration(
                    color: _isLoading ? Colors.grey : const Color(0xFF7EB5A6),
                    shape: BoxShape.circle,
                  ),
                  child: IconButton(
                    icon: const Icon(Icons.send, color: Colors.white),
                    onPressed: _isLoading ? null : _sendMessage,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}