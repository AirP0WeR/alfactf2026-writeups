.class Lio/peakmood/mobile/MainActivity$7$2;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lio/peakmood/mobile/MainActivity$7;->run()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$1:Lio/peakmood/mobile/MainActivity$7;

.field final synthetic val$node:Lorg/json/JSONObject;


# direct methods
.method constructor <init>(Lio/peakmood/mobile/MainActivity$7;Lorg/json/JSONObject;)V
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

    .line 643
    iput-object p1, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iput-object p2, p0, Lio/peakmood/mobile/MainActivity$7$2;->val$node:Lorg/json/JSONObject;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .locals 8

    .line 646
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    const/4 v1, 0x0

    invoke-static {v0, v1}, Lio/peakmood/mobile/MainActivity;->access$1602(Lio/peakmood/mobile/MainActivity;Z)Z

    .line 647
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$7$2;->val$node:Lorg/json/JSONObject;

    iget-object v3, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iget-object v3, v3, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v3}, Lio/peakmood/mobile/MainActivity;->access$1800(Lio/peakmood/mobile/MainActivity;)I

    move-result v3

    const-string v4, "hits_left"

    invoke-virtual {v2, v4, v3}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result v2

    invoke-static {v0, v2}, Lio/peakmood/mobile/MainActivity;->access$1802(Lio/peakmood/mobile/MainActivity;I)I

    .line 648
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0}, Lio/peakmood/mobile/MainActivity;->access$2000(Lio/peakmood/mobile/MainActivity;)Landroid/widget/ProgressBar;

    move-result-object v0

    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iget-object v2, v2, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v2}, Lio/peakmood/mobile/MainActivity;->access$1900(Lio/peakmood/mobile/MainActivity;)I

    move-result v2

    iget-object v3, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iget-object v3, v3, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v3}, Lio/peakmood/mobile/MainActivity;->access$1800(Lio/peakmood/mobile/MainActivity;)I

    move-result v3

    sub-int/2addr v2, v3

    invoke-virtual {v0, v2}, Landroid/widget/ProgressBar;->setProgress(I)V

    .line 649
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0}, Lio/peakmood/mobile/MainActivity;->access$2100(Lio/peakmood/mobile/MainActivity;)V

    .line 650
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0}, Lio/peakmood/mobile/MainActivity;->access$2200(Lio/peakmood/mobile/MainActivity;)V

    .line 651
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0}, Lio/peakmood/mobile/MainActivity;->access$1800(Lio/peakmood/mobile/MainActivity;)I

    move-result v0

    if-nez v0, :cond_0

    .line 652
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    const-string v1, "\u0412\u043d\u0443\u0442\u0440\u0435\u043d\u043d\u0438\u0439 \u0441\u043b\u043e\u0439 \u043e\u0442\u043a\u0440\u044b\u0442. \u0422\u0430\u043f\u043d\u0438 \u043f\u043e \u0436\u0435\u043e\u0434\u0435 \u0435\u0449\u0451 \u0440\u0430\u0437, \u0447\u0442\u043e\u0431\u044b \u0437\u0430\u0431\u0440\u0430\u0442\u044c \u043e\u0431\u0440\u0430\u0437\u0435\u0446."

    const-string v2, "\u0413\u041e\u0422\u041e\u0412\u041e"

    const-string v3, "\u0416\u0435\u043e\u0434\u0430 \u0440\u0430\u0441\u043a\u0440\u044b\u0442\u0430"

    invoke-static {v0, v3, v1, v2}, Lio/peakmood/mobile/MainActivity;->access$1000(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    goto :goto_0

    .line 654
    :cond_0
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    sget-object v2, Ljava/util/Locale;->US:Ljava/util/Locale;

    iget-object v3, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iget-object v3, v3, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    .line 656
    invoke-static {v3}, Lio/peakmood/mobile/MainActivity;->access$1800(Lio/peakmood/mobile/MainActivity;)I

    move-result v3

    invoke-static {v3}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v3

    const/4 v4, 0x1

    new-array v5, v4, [Ljava/lang/Object;

    aput-object v3, v5, v1

    const-string v3, "\u041e\u0441\u0442\u0430\u043b\u043e\u0441\u044c \u0443\u0434\u0430\u0440\u043e\u0432: %d. \u041f\u0440\u043e\u0434\u043e\u043b\u0436\u0430\u0439 \u0431\u0438\u0442\u044c \u043f\u043e \u0436\u0435\u043e\u0434\u0435."

    invoke-static {v2, v3, v5}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v2

    sget-object v3, Ljava/util/Locale;->US:Ljava/util/Locale;

    iget-object v5, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iget-object v5, v5, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    .line 657
    invoke-static {v5}, Lio/peakmood/mobile/MainActivity;->access$1900(Lio/peakmood/mobile/MainActivity;)I

    move-result v5

    iget-object v6, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iget-object v6, v6, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v6}, Lio/peakmood/mobile/MainActivity;->access$1800(Lio/peakmood/mobile/MainActivity;)I

    move-result v6

    sub-int/2addr v5, v6

    invoke-static {v5}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v5

    iget-object v6, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iget-object v6, v6, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v6}, Lio/peakmood/mobile/MainActivity;->access$1900(Lio/peakmood/mobile/MainActivity;)I

    move-result v6

    invoke-static {v6}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v6

    const/4 v7, 0x2

    new-array v7, v7, [Ljava/lang/Object;

    aput-object v5, v7, v1

    aput-object v6, v7, v4

    const-string v1, "\u0423\u0414\u0410\u0420 %d/%d"

    invoke-static {v3, v1, v7}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v1

    .line 654
    const-string v3, "\u041c\u0438\u043d\u0435\u0440\u0430\u043b \u043f\u043e\u0434\u0434\u0430\u0451\u0442\u0441\u044f"

    invoke-static {v0, v3, v2, v1}, Lio/peakmood/mobile/MainActivity;->access$1000(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    .line 660
    :goto_0
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$7$2;->this$1:Lio/peakmood/mobile/MainActivity$7;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$7;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0}, Lio/peakmood/mobile/MainActivity;->access$900(Lio/peakmood/mobile/MainActivity;)V

    .line 661
    return-void
.end method
