package com.daledou;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;

import org.json.JSONArray;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class TestActivity extends AppCompatActivity {

    private LinearLayout accountListContainer;
    private TextView tvGlobalStatus, tvResponseLog;
    private ScrollView logScrollView;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler handler = new Handler(Looper.getMainLooper());

    // 账号卡片列表
    private final List<AccountCard> cards = new ArrayList<>();

    static class AccountCard {
        String qq;
        View root;
        TextView tvQQ, tvStatusBadge, tvMsg, tvName, tvLevel, tvHP, tvPower;
        View rowInfo;
        Button btnTest;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_test);

        accountListContainer = findViewById(R.id.accountListContainer);
        tvGlobalStatus       = findViewById(R.id.tvGlobalStatus);
        tvResponseLog        = findViewById(R.id.tvResponseLog);
        logScrollView        = findViewById(R.id.logScrollView);

        findViewById(R.id.btnBack).setOnClickListener(v -> finish());
        findViewById(R.id.btnTestAll).setOnClickListener(v -> testAll());
        findViewById(R.id.btnClearLog).setOnClickListener(v -> {
            tvResponseLog.setText("");
        });

        loadAccountCards();
    }

    private void loadAccountCards() {
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                String qqRaw = bridge.callAttr("get_qq_list").toString();
                handler.post(() -> buildCards(qqRaw));
            } catch (Exception e) {
                handler.post(() -> tvGlobalStatus.setText("❌ 加载账号失败: " + e.getMessage()));
            }
        });
    }

    private void buildCards(String qqRaw) {
        accountListContainer.removeAllViews();
        cards.clear();

        if (qqRaw == null || qqRaw.trim().isEmpty()) {
            tvGlobalStatus.setText("⚠️ 未配置任何账号，请先配置 Cookie");
            return;
        }

        String[] qqArr = qqRaw.split(",");
        tvGlobalStatus.setText("共 " + qqArr.length + " 个账号，点击\"测试\"或\"测试全部\"");

        LayoutInflater inflater = LayoutInflater.from(this);

        for (String qq : qqArr) {
            qq = qq.trim();
            if (qq.isEmpty()) continue;

            View row = inflater.inflate(R.layout.item_account_test, accountListContainer, false);
            AccountCard card = new AccountCard();
            card.qq = qq;
            card.root = row;
            card.tvQQ          = row.findViewById(R.id.tvQQ);
            card.tvStatusBadge = row.findViewById(R.id.tvStatusBadge);
            card.tvMsg         = row.findViewById(R.id.tvMsg);
            card.tvName        = row.findViewById(R.id.tvName);
            card.tvLevel       = row.findViewById(R.id.tvLevel);
            card.tvHP          = row.findViewById(R.id.tvHP);
            card.tvPower       = row.findViewById(R.id.tvPower);
            card.rowInfo       = row.findViewById(R.id.rowInfo);
            card.btnTest       = row.findViewById(R.id.btnTestSingle);

            card.tvQQ.setText("QQ: " + qq);

            final String finalQQ = qq;
            card.btnTest.setOnClickListener(v -> testSingle(finalQQ));

            cards.add(card);
            accountListContainer.addView(row);
        }
    }

    private void testSingle(String qq) {
        AccountCard card = findCard(qq);
        if (card == null) return;

        setCardLoading(card);
        appendLog("⏳ [" + now() + "] 测试账号 " + qq + " ...");

        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                String json = bridge.callAttr("test_account", qq).toString();
                handler.post(() -> {
                    updateCard(card, json);
                    appendLog(buildLogLine(qq, json));
                });
            } catch (Exception e) {
                handler.post(() -> {
                    setCardError(card, "调用异常: " + e.getMessage());
                    appendLog("❌ [" + now() + "] " + qq + " 异常: " + e.getMessage());
                });
            }
        });
    }

    private void testAll() {
        tvGlobalStatus.setText("⏳ 正在测试所有账号...");
        appendLog("\n===== [" + now() + "] 开始全部测试 =====");

        // 先把所有卡片设为 loading
        for (AccountCard card : cards) setCardLoading(card);

        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                String json = bridge.callAttr("test_all_accounts").toString();
                handler.post(() -> {
                    try {
                        JSONArray arr = new JSONArray(json);
                        int ok = 0, fail = 0;
                        for (int i = 0; i < arr.length(); i++) {
                            JSONObject obj = arr.getJSONObject(i);
                            String qq = obj.getString("qq");
                            AccountCard card = findCard(qq);
                            if (card != null) {
                                updateCard(card, obj.toString());
                            }
                            appendLog(buildLogLine(qq, obj.toString()));
                            if ("ok".equals(obj.optString("status"))) ok++;
                            else fail++;
                        }
                        tvGlobalStatus.setText("✅ 测试完成：" + ok + " 成功 / " + fail + " 失败");
                    } catch (Exception e) {
                        tvGlobalStatus.setText("❌ 解析结果失败: " + e.getMessage());
                    }
                });
            } catch (Exception e) {
                handler.post(() -> tvGlobalStatus.setText("❌ 测试失败: " + e.getMessage()));
            }
        });
    }

    // ---- 卡片更新工具方法 ----

    private void setCardLoading(AccountCard card) {
        card.tvStatusBadge.setText("测试中...");
        card.tvStatusBadge.setBackgroundResource(R.drawable.bg_tag_grey);
        card.tvStatusBadge.setTextColor(0xFFFFEB3B);
        card.tvMsg.setText("");
        card.rowInfo.setVisibility(View.GONE);
        card.btnTest.setEnabled(false);
    }

    private void setCardError(AccountCard card, String msg) {
        card.tvStatusBadge.setText("异常");
        card.tvStatusBadge.setBackgroundResource(R.drawable.bg_btn_red);
        card.tvStatusBadge.setTextColor(0xFFFFFFFF);
        card.tvMsg.setText("❌ " + msg);
        card.tvMsg.setTextColor(0xFFE74C3C);
        card.rowInfo.setVisibility(View.GONE);
        card.btnTest.setEnabled(true);
    }

    private void updateCard(AccountCard card, String json) {
        card.btnTest.setEnabled(true);
        try {
            JSONObject obj = new JSONObject(json);
            String status = obj.optString("status", "error");
            String msg    = obj.optString("msg", "");
            String name   = obj.optString("name", "");
            String level  = obj.optString("level", "");
            String hp     = obj.optString("hp", "");
            String power  = obj.optString("power", "");
            String gold   = obj.optString("gold", "");

            if ("ok".equals(status)) {
                card.tvStatusBadge.setText("✅ 正常");
                card.tvStatusBadge.setBackgroundResource(R.drawable.bg_tag_green);
                card.tvStatusBadge.setTextColor(0xFF98FB98);
                card.tvMsg.setText(msg);
                card.tvMsg.setTextColor(0xFF2ECC71);
                card.rowInfo.setVisibility(View.VISIBLE);
                card.tvName.setText("角色名: " + (name.isEmpty() ? "—" : name));
                card.tvLevel.setText("等级: " + (level.isEmpty() ? "—" : level));
                card.tvHP.setText("体力: " + (hp.isEmpty() ? "—" : hp));
                card.tvPower.setText("战力: " + (power.isEmpty() ? "—" : power));
            } else if ("fail".equals(status)) {
                card.tvStatusBadge.setText("❌ 失效");
                card.tvStatusBadge.setBackgroundResource(R.drawable.bg_btn_red);
                card.tvStatusBadge.setTextColor(0xFFFFFFFF);
                card.tvMsg.setText(msg);
                card.tvMsg.setTextColor(0xFFE74C3C);
                card.rowInfo.setVisibility(View.GONE);
            } else {
                card.tvStatusBadge.setText("⚠️ 错误");
                card.tvStatusBadge.setBackgroundResource(R.drawable.bg_tag_grey);
                card.tvStatusBadge.setTextColor(0xFFFFEB3B);
                card.tvMsg.setText(msg);
                card.tvMsg.setTextColor(0xFFF39C12);
                card.rowInfo.setVisibility(View.GONE);
            }
        } catch (Exception e) {
            setCardError(card, "解析失败: " + e.getMessage());
        }
    }

    // ---- 日志工具 ----

    private void appendLog(String line) {
        String current = tvResponseLog.getText().toString();
        tvResponseLog.setText(current + "\n" + line);
        logScrollView.post(() -> logScrollView.fullScroll(ScrollView.FOCUS_DOWN));
    }

    private String buildLogLine(String qq, String json) {
        try {
            JSONObject obj = new JSONObject(json);
            String status = obj.optString("status", "error");
            String icon = "ok".equals(status) ? "✅" : ("fail".equals(status) ? "❌" : "⚠️");
            String name = obj.optString("name", "");
            String level = obj.optString("level", "");
            String hp = obj.optString("hp", "");
            String msg = obj.optString("msg", "");
            if ("ok".equals(status)) {
                return icon + " [" + now() + "] " + qq
                    + " | 角色:" + name
                    + " | Lv." + level
                    + " | 体力:" + hp
                    + " | " + msg;
            } else {
                return icon + " [" + now() + "] " + qq + " | " + msg;
            }
        } catch (Exception e) {
            return "⚠️ [" + now() + "] " + qq + " | 解析失败";
        }
    }

    private AccountCard findCard(String qq) {
        for (AccountCard c : cards) {
            if (c.qq.equals(qq)) return c;
        }
        return null;
    }

    private String now() {
        return new SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(new Date());
    }
}
