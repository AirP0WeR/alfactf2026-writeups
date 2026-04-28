.class Lio/peakmood/mobile/MainActivity$9;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lio/peakmood/mobile/MainActivity;->showError(Ljava/lang/String;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lio/peakmood/mobile/MainActivity;

.field final synthetic val$message:Ljava/lang/String;


# direct methods
.method constructor <init>(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;)V
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

    .line 784
    iput-object p1, p0, Lio/peakmood/mobile/MainActivity$9;->this$0:Lio/peakmood/mobile/MainActivity;

    iput-object p2, p0, Lio/peakmood/mobile/MainActivity$9;->val$message:Ljava/lang/String;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .locals 4

    .line 787
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$9;->this$0:Lio/peakmood/mobile/MainActivity;

    const/4 v1, 0x0

    invoke-static {v0, v1}, Lio/peakmood/mobile/MainActivity;->access$2602(Lio/peakmood/mobile/MainActivity;Z)Z

    .line 788
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$9;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0, v1}, Lio/peakmood/mobile/MainActivity;->access$1602(Lio/peakmood/mobile/MainActivity;Z)Z

    .line 789
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$9;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0, v1}, Lio/peakmood/mobile/MainActivity;->access$2302(Lio/peakmood/mobile/MainActivity;Z)Z

    .line 790
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$9;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0}, Lio/peakmood/mobile/MainActivity;->access$900(Lio/peakmood/mobile/MainActivity;)V

    .line 791
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$9;->this$0:Lio/peakmood/mobile/MainActivity;

    iget-object v1, p0, Lio/peakmood/mobile/MainActivity$9;->val$message:Ljava/lang/String;

    const-string v2, "\u041d\u0415\u0422 \u0421\u0412\u042f\u0417\u0418"

    const-string v3, "\u0421\u0435\u0440\u0432\u0438\u0441 \u043d\u0435\u0434\u043e\u0441\u0442\u0443\u043f\u0435\u043d"

    invoke-static {v0, v3, v1, v2}, Lio/peakmood/mobile/MainActivity;->access$1000(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    .line 792
    return-void
.end method
