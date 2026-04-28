.class Lio/peakmood/mobile/MainActivity$8$2;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lio/peakmood/mobile/MainActivity$8;->run()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$1:Lio/peakmood/mobile/MainActivity$8;

.field final synthetic val$loot:Lorg/json/JSONObject;


# direct methods
.method constructor <init>(Lio/peakmood/mobile/MainActivity$8;Lorg/json/JSONObject;)V
    .locals 0
    .annotation system Ldalvik/annotation/MethodParameters;
        accessFlags = {
            0x8010,
            0x1010
        }
        names = {
            null,
            null
        }
    .end annotation

    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .line 701
    iput-object p1, p0, Lio/peakmood/mobile/MainActivity$8$2;->this$1:Lio/peakmood/mobile/MainActivity$8;

    iput-object p2, p0, Lio/peakmood/mobile/MainActivity$8$2;->val$loot:Lorg/json/JSONObject;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .locals 7

    .line 704
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$8$2;->this$1:Lio/peakmood/mobile/MainActivity$8;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$8;->this$0:Lio/peakmood/mobile/MainActivity;

    const/4 v1, 0x0

    invoke-static {v0, v1}, Lio/peakmood/mobile/MainActivity;->access$2302(Lio/peakmood/mobile/MainActivity;Z)Z

    .line 705
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$8$2;->this$1:Lio/peakmood/mobile/MainActivity$8;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$8;->this$0:Lio/peakmood/mobile/MainActivity;

    iget-object v1, p0, Lio/peakmood/mobile/MainActivity$8$2;->val$loot:Lorg/json/JSONObject;

    .line 706
    const-string v2, "display_name"

    const-string v3, "\u0414\u043e\u0431\u044b\u0447\u0430 \u043f\u043e\u043b\u0443\u0447\u0435\u043d\u0430"

    invoke-virtual {v1, v2, v3}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$8$2;->val$loot:Lorg/json/JSONObject;

    .line 707
    const-string v3, "flavor"

    const-string v4, ""

    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    .line 705
    const-string v3, "\u0414\u041e\u0411\u042b\u0422\u041e"

    invoke-static {v0, v1, v2, v3}, Lio/peakmood/mobile/MainActivity;->access$1000(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    .line 711
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    .line 712
    const-string v1, "\u0420\u0435\u0434\u043a\u043e\u0441\u0442\u044c: "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$8$2;->this$1:Lio/peakmood/mobile/MainActivity$8;

    iget-object v2, v2, Lio/peakmood/mobile/MainActivity$8;->this$0:Lio/peakmood/mobile/MainActivity;

    iget-object v3, p0, Lio/peakmood/mobile/MainActivity$8$2;->val$loot:Lorg/json/JSONObject;

    const-string v5, "tier"

    const-string v6, "unknown"

    invoke-virtual {v3, v5, v6}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    invoke-static {v2, v3}, Lio/peakmood/mobile/MainActivity;->access$2400(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 713
    iget-object v1, p0, Lio/peakmood/mobile/MainActivity$8$2;->val$loot:Lorg/json/JSONObject;

    const-string v2, "artifact_signature"

    invoke-virtual {v1, v2}, Lorg/json/JSONObject;->has(Ljava/lang/String;)Z

    move-result v1

    if-eqz v1, :cond_0

    .line 714
    nop

    .line 715
    const-string v1, "\n\n"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    iget-object v3, p0, Lio/peakmood/mobile/MainActivity$8$2;->this$1:Lio/peakmood/mobile/MainActivity$8;

    iget-object v3, v3, Lio/peakmood/mobile/MainActivity$8;->this$0:Lio/peakmood/mobile/MainActivity;

    .line 716
    const v5, 0x7f06000f

    invoke-virtual {v3, v5}, Lio/peakmood/mobile/MainActivity;->getString(I)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    .line 717
    const-string v3, ": "

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    iget-object v3, p0, Lio/peakmood/mobile/MainActivity$8$2;->val$loot:Lorg/json/JSONObject;

    .line 718
    invoke-virtual {v3, v2, v4}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    .line 720
    :cond_0
    iget-object v1, p0, Lio/peakmood/mobile/MainActivity$8$2;->this$1:Lio/peakmood/mobile/MainActivity$8;

    iget-object v1, v1, Lio/peakmood/mobile/MainActivity$8;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v1, v0}, Lio/peakmood/mobile/MainActivity;->access$2500(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;)V

    .line 721
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$8$2;->this$1:Lio/peakmood/mobile/MainActivity$8;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$8;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0}, Lio/peakmood/mobile/MainActivity;->access$1700(Lio/peakmood/mobile/MainActivity;)V

    .line 722
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$8$2;->this$1:Lio/peakmood/mobile/MainActivity$8;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$8;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0}, Lio/peakmood/mobile/MainActivity;->access$300(Lio/peakmood/mobile/MainActivity;)V

    .line 723
    return-void
.end method
